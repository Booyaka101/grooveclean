"""Click detection: a dilated 1-D CNN over a rate-normalised copy of the signal.

Every window in here is defined in milliseconds. The network has a fixed receptive field in
samples, so the signal is resampled to ANALYSIS_RATE before inference and the spans are
mapped back afterwards; that is what makes 44.1k and 192k behave the same.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

ANALYSIS_RATE = 44100
NORM_MS = 100.0  # local level/DC window
FLOOR_MS = 50.0  # window for the native-rate impulse noise floor
GUARD_MS = 0.2  # slack when mapping an analysis-rate span back to native rate
INFER_CHUNK = 5 * ANALYSIS_RATE

WEIGHTS_PATH = Path(__file__).resolve().parent / "weights" / "detector.pt"


class DetectorError(Exception):
    pass


# --------------------------------------------------------------------------- signal helpers


def resample(x: torch.Tensor, n_out: int) -> torch.Tensor:
    """Band-limited resample along the last axis (the FFT method, as scipy.signal.resample)."""
    n_in = x.shape[-1]
    if n_out == n_in:
        return x
    spec = torch.fft.rfft(x.to(torch.float32), dim=-1)
    nb_out = n_out // 2 + 1
    if nb_out <= spec.shape[-1]:
        # An even output length leaves the Nyquist bin unpaired; it has to absorb both
        # halves of the pair it came from, or the top octave loses 6 dB.
        out = spec[..., :nb_out].clone()
        if n_out % 2 == 0:
            out[..., -1] = out[..., -1] * 2.0
    else:
        out = torch.zeros(*spec.shape[:-1], nb_out, dtype=spec.dtype, device=x.device)
        out[..., : spec.shape[-1]] = spec
        if n_in % 2 == 0:
            out[..., n_in // 2] *= 0.5
    return torch.fft.irfft(out, n=n_out, dim=-1) * (n_out / n_in)


def box_mean(x: torch.Tensor, width: int) -> torch.Tensor:
    """Centred moving average along the last axis, O(n) via cumsum in float64."""
    width = max(1, width | 1)
    pad = width // 2
    flat = x.reshape(-1, x.shape[-1]).to(torch.float64)
    xp = F.pad(flat[:, None, :], (pad, pad), mode="reflect")[:, 0, :]
    c = F.pad(torch.cumsum(xp, dim=-1), (1, 0))
    return ((c[..., width:] - c[..., :-width]) / width).reshape(x.shape).to(x.dtype)


def normalize(x: torch.Tensor, rate: int) -> torch.Tensor:
    """Remove DC and local level, then compress. ``x`` is [..., n] at ``rate``.

    asinh rather than a hard clip: a 60 dB pop and a 6 dB tick stay on the same input scale
    without either saturating, so the network sees shape rather than amplitude.
    """
    width = max(3, int(round(NORM_MS * 1e-3 * rate)) | 1)
    centred = x - box_mean(x, width)
    level = torch.sqrt(box_mean(centred * centred, width).clamp_min(0.0))
    floor = torch.clamp(centred.abs().amax(dim=-1, keepdim=True) * 1e-4, min=1e-9)
    return torch.asinh(centred / torch.clamp(level, min=floor))


CLIP_K = 2.5  # impulses above this many local means stop counting towards the local mean
CLIP_BIAS = 0.9783  # E[min(|N|, CLIP_K E|N|)] / E[|N|], so Gaussian noise still scores 1.0


def impulsiveness(x: torch.Tensor, rate: int) -> torch.Tensor:
    """Second-difference magnitude over a robust local scale: 1.0 means "typical for here".

    The scale is a clipped local mean, not an RMS. Under dense crackle the plain moving RMS is
    set by the crackle itself, so every tick scores about 1 and none of them stand out.
    """
    d = torch.zeros_like(x)
    d[..., 1:-1] = (x[..., 2:] - 2.0 * x[..., 1:-1] + x[..., :-2]).abs()
    width = max(3, int(round(FLOOR_MS * 1e-3 * rate)) | 1)
    scale = box_mean(d, width)
    for _ in range(2):
        scale = box_mean(torch.minimum(d, CLIP_K * scale), width) / CLIP_BIAS
    floor = torch.clamp(d.amax(dim=-1, keepdim=True) * 1e-6, min=1e-12)
    return d / scale.clamp_min(floor)


def clipped(x: np.ndarray, min_run: int = 3, dilate: int = 2) -> np.ndarray:
    """Flat-topped runs at the signal's own peak. A square edge is impulsive but is not a click."""
    n = x.shape[-1]
    peak = float(np.max(np.abs(x))) if n else 0.0
    if peak <= 0.0 or n < min_run:
        return np.zeros(n, dtype=bool)
    at_peak = np.abs(x) >= peak * (1.0 - 1e-9)
    run = at_peak[: n - min_run + 1].copy()
    for k in range(1, min_run):
        run &= at_peak[k : n - min_run + 1 + k]
    mask = np.zeros(n, dtype=bool)
    for k in range(min_run):
        mask[k : n - min_run + 1 + k] |= run
    grown = mask.copy()
    for k in range(1, dilate + 1):
        grown[k:] |= mask[:-k]
        grown[:-k] |= mask[k:]
    return grown


# --------------------------------------------------------------------------- model


class ResBlock(nn.Module):
    def __init__(self, channels: int, kernel: int, dilation: int):
        super().__init__()
        self.conv = nn.Conv1d(
            channels, channels, kernel, dilation=dilation, padding=dilation * (kernel // 2)
        )
        self.norm = nn.BatchNorm1d(channels)
        self.mix = nn.Conv1d(channels, channels, 1)
        self.norm2 = nn.BatchNorm1d(channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = F.relu(self.norm(self.conv(x)))
        return F.relu(x + self.norm2(self.mix(h)))


class ClickCNN(nn.Module):
    """Fully convolutional: one click probability per input sample, any input length."""

    def __init__(self, channels: int = 32, blocks: int = 8, kernel: int = 9):
        super().__init__()
        self.config = {"channels": channels, "blocks": blocks, "kernel": kernel}
        self.stem = nn.Conv1d(1, channels, kernel, padding=kernel // 2)
        self.blocks = nn.ModuleList([ResBlock(channels, kernel, 2**i) for i in range(blocks)])
        self.head = nn.Sequential(
            nn.Conv1d(channels, channels, 1), nn.ReLU(), nn.Conv1d(channels, 1, 1)
        )
        self.receptive_field = 1 + (kernel - 1) * (2**blocks - 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.stem(x)
        for block in self.blocks:
            h = block(h)
        return self.head(h).squeeze(1)


# --------------------------------------------------------------------------- thresholds

SENSITIVITY_SPREAD = 8.0  # logit units across the full 0..1 knob


def _logit(p: float) -> float:
    p = min(max(p, 1e-6), 1.0 - 1e-6)
    return math.log(p / (1.0 - p))


def _sigmoid(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))


def thresholds(sensitivity: float, cal_hi: float, cal_lo: float) -> tuple[float, float, float]:
    """Map the 0..1 knob onto (enter, leave, native impulse gate). 0.5 is the trained point."""
    s = min(max(float(sensitivity), 0.0), 1.0)
    shift = SENSITIVITY_SPREAD * (0.5 - s)
    gate = 3.0 * math.exp(1.4 * (0.5 - s))
    return _sigmoid(_logit(cal_hi) + shift), _sigmoid(_logit(cal_lo) + shift), gate


# --------------------------------------------------------------------------- spans


def hysteresis(prob: np.ndarray, hi: float, lo: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Runs above ``lo`` that peak above ``hi``. Returns (starts, ends, peak probability)."""
    above = np.concatenate(([False], prob >= lo, [False]))
    edges = np.diff(above.astype(np.int8))
    starts = np.flatnonzero(edges == 1)
    ends = np.flatnonzero(edges == -1)
    if starts.size == 0:
        empty = np.zeros(0, dtype=np.int64)
        return empty, empty, np.zeros(0, dtype=np.float32)
    bounds = np.empty(starts.size * 2, dtype=np.int64)
    bounds[0::2] = starts
    bounds[1::2] = ends
    peak = np.maximum.reduceat(np.concatenate((prob, [0.0])), bounds)[0::2]
    keep = peak >= hi
    return starts[keep], ends[keep], peak[keep].astype(np.float32)


def merge_spans(starts: np.ndarray, ends: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Collapse overlapping or touching spans.

    Returns (starts, ends, at) where ``at`` indexes the input span that opened each output
    span, so per-span values like confidence can be reduced over the same groups.
    """
    if starts.size == 0:
        return starts, ends, np.zeros(0, dtype=np.int64)
    first = np.concatenate(([True], starts[1:] > ends[:-1]))
    at = np.flatnonzero(first)
    return starts[first], np.maximum.reduceat(ends, at), at


def to_native(
    starts: np.ndarray, ends: np.ndarray, rate: int, frames: int
) -> tuple[np.ndarray, np.ndarray]:
    ratio = rate / ANALYSIS_RATE
    guard = max(1, int(round(GUARD_MS * 1e-3 * rate)))
    s = np.maximum(0, np.floor(starts * ratio).astype(np.int64) - guard)
    e = np.minimum(frames, np.ceil(ends * ratio).astype(np.int64) + guard)
    return s, e


def trim_to_active(
    starts: np.ndarray, ends: np.ndarray, active: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Shrink each span to the impulsive samples inside it; drop spans containing none.

    The CNN localises to about 23 us; this pins the edges at the native rate so the
    difference file holds the tick and not the music either side of it.
    """
    keep = np.zeros(starts.size, dtype=bool)
    idx = np.flatnonzero(active)
    if idx.size == 0 or starts.size == 0:
        return starts[:0], ends[:0], keep
    first = np.searchsorted(idx, starts, side="left")
    last = np.searchsorted(idx, ends, side="left") - 1
    keep = first <= last
    return idx[first[keep]], idx[last[keep]] + 1, keep


def active_mask(x: np.ndarray, rate: int, gate: float) -> np.ndarray:
    """Samples impulsive enough to belong to a click, minus any clipped run."""
    impulsive = impulsiveness(torch.from_numpy(x.astype(np.float32)), rate).numpy()
    return (impulsive >= gate) & ~clipped(x)


def spans(
    prob: np.ndarray, active: np.ndarray, rate: int, hi: float, lo: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Click spans for one channel at the native rate, with their peak probabilities.

    ``prob`` is at ANALYSIS_RATE and ``active`` is at ``rate``; the mapping between them is
    the whole reason both live here rather than in the caller.
    """
    starts, ends, peak = hysteresis(prob, hi, lo)
    if starts.size == 0:
        return starts, ends, peak
    starts, ends = to_native(starts, ends, rate, active.size)
    starts, ends, at = merge_spans(starts, ends)
    peak = np.maximum.reduceat(peak, at)

    starts, ends, keep = trim_to_active(starts, ends, active)
    peak = peak[keep]
    if starts.size == 0:
        return starts, ends, peak
    starts, ends, at = merge_spans(starts, ends)
    return starts, ends, np.maximum.reduceat(peak, at)


# --------------------------------------------------------------------------- detector


@dataclass(slots=True)
class Calibration:
    hi: float
    lo: float


def resolve_device(device: str | torch.device | None) -> torch.device:
    """cuda when asked for and available, else cpu. Never fail because a GPU is missing."""
    if device is None or str(device) == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dev = torch.device(device)
    if dev.type == "cuda" and not torch.cuda.is_available():
        return torch.device("cpu")
    return dev


class Detector:
    def __init__(self, model: ClickCNN, calibration: Calibration, device: torch.device):
        self.model = model.to(device).eval()
        self.calibration = calibration
        self.device = device

    @classmethod
    def load(
        cls, path: str | Path | None = None, device: str | torch.device | None = None
    ) -> Detector:
        path = Path(path or WEIGHTS_PATH)
        if not path.exists():
            raise DetectorError(
                f"detector weights not found at {path}. A source checkout needs "
                "python train/train.py first; an installed wheel ships them."
            )
        try:
            blob = torch.load(str(path), map_location="cpu", weights_only=True)
        except Exception as exc:
            raise DetectorError(f"{path}: cannot be read as a PyTorch checkpoint") from exc
        try:
            model = ClickCNN(**blob["config"])
            model.load_state_dict(blob["state_dict"])
            calibration = Calibration(**blob["calibration"])
        except (KeyError, TypeError, RuntimeError) as exc:
            raise DetectorError(f"{path}: not a grooveclean detector checkpoint ({exc})") from exc
        return cls(model, calibration, resolve_device(device))

    @torch.no_grad()
    def probabilities(self, x: torch.Tensor, rate: int) -> torch.Tensor:
        """``x`` is [channels, frames] in [-1, 1] at ``rate``; returns [channels, n] at 44.1 kHz."""
        x = x.to(self.device, torch.float32)
        n_out = max(1, int(round(x.shape[-1] * ANALYSIS_RATE / rate)))
        xn = normalize(resample(x, n_out), ANALYSIS_RATE)
        pad = self.model.receptive_field
        out = torch.empty_like(xn)
        for start in range(0, n_out, INFER_CHUNK):
            stop = min(n_out, start + INFER_CHUNK)
            lo, hi = max(0, start - pad), min(n_out, stop + pad)
            logits = self.model(xn[:, None, lo:hi])
            out[:, start:stop] = logits[:, start - lo : start - lo + (stop - start)]
        return torch.sigmoid(out)
