"""Harvest real click waveforms from the Internet Archive's 78rpm collection.

A 78 side has almost no musical energy above 10 kHz, so the band above it holds surface noise
and clicks and nothing else. Impulses are located there, then the click waveform itself is
taken as the LSAR residual over the full band: what the interpolator removes is the tick, and
what it leaves is the music. That yields hundreds of real clicks per side instead of the
handful sitting in the lead-in groove, and each one is a standalone waveform that can be added
to clean audio with an exact ground-truth mask.

How big a residual counts as a click is calibrated per transfer, by running the same
interpolation over randomly chosen click-free spans and taking a high percentile of that.

Quiet regions are still gated by level, because a stretch of groove noise has to be genuinely
music-free to be usable as a surface-noise bed.

Only FLAC items are used. Much of the collection is VBR-MP3-only and the codec ringing around
an impulse is exactly the shape this detector must not learn.

    python train/harvest_noise.py --items 400 --out corpus/noise
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _ia  # noqa: E402
from grooveclean import detect, repair  # noqa: E402

COLLECTION = _ia.Collection(
    query='collection:"78rpm" AND format:"Flac"',
    rows=2000,
    fields=["identifier"],
    label="noise",
    banner="78rpm+FLAC",
)

HP_LO, HP_HI = 10000.0, 12000.0  # raised-cosine transition into the click-only band
MAX_HF_FRACTION = 0.35  # above this the item is not a 78 transfer, it has real treble
MIN_SOURCE_RATE = 30000  # below it there is no click-only band left to look in

PEAK_GATE = 12.0
EDGE_GATE = 3.0
PAD_MS = 0.1
MIN_CLICK_SAMPLES = 2
MAX_CLICK_MS = 20.0
MAX_CLICKS = 2000

CONTROL_EVERY = 50  # one calibration span per this many click-free samples
CONTROL_PCT = 99.0
EDGE_FRACTION = 0.25  # a span still this hot at its own edge was cut short, so drop it

FRAME_MS = 10.0
MIN_QUIET_MS = 200.0
QUIET_DB = 30.0
BED_SAMPLES = detect.ANALYSIS_RATE // 4
MAX_BEDS = 12
DIGITAL_SILENCE = 1e-6

WHOLE_FILE_BYTES = 20 << 20  # below this, take the side entire
HEAD_BYTES = 12 << 20        # above it, take only the front


def highpass(x: np.ndarray, rate: int) -> np.ndarray:
    """Zero-phase brick wall with a raised-cosine skirt from HP_LO to HP_HI."""
    spec = np.fft.rfft(x)
    freq = np.fft.rfftfreq(x.size, 1.0 / rate)
    ramp = np.clip((freq - HP_LO) / (HP_HI - HP_LO), 0.0, 1.0)
    return np.fft.irfft(spec * (0.5 - 0.5 * np.cos(np.pi * ramp)), n=x.size)


def candidate_spans(hf: np.ndarray, rate: int, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Impulses in the click-only band, padded, merged, and clear of the array edges."""
    imp = detect.impulsiveness(torch.from_numpy(hf.astype(np.float32)), rate).numpy()
    starts, ends, _ = detect.hysteresis(imp, PEAK_GATE, EDGE_GATE)
    width = ends - starts
    keep = (width >= MIN_CLICK_SAMPLES) & (width <= int(round(MAX_CLICK_MS * 1e-3 * rate)))
    starts, ends = starts[keep], ends[keep]
    if starts.size == 0:
        return starts, ends
    pad = max(1, int(round(PAD_MS * 1e-3 * rate)))
    return merge(np.maximum(0, starts - pad), np.minimum(n, ends + pad), repair.CONTEXT, n)


def merge(
    starts: np.ndarray, ends: np.ndarray, margin: int, n: int
) -> tuple[np.ndarray, np.ndarray]:
    """Collapse overlapping spans and drop any without ``margin`` samples of room either side."""
    starts, ends, _ = detect.merge_spans(starts, ends)
    room = (starts >= margin) & (ends <= n - margin)
    return starts[room], ends[room]


def control_spans(
    n: int, taken: np.ndarray, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """Click-free spans of click-like width, for calibrating what a real residual looks like."""
    free = np.flatnonzero(~taken)
    free = free[(free >= repair.CONTEXT) & (free < n - repair.CONTEXT - 16)]
    count = free.size // CONTROL_EVERY
    if count < 32:
        return np.zeros(0, np.int64), np.zeros(0, np.int64)
    starts = np.sort(rng.choice(free, count, replace=False))
    return merge(starts, starts + rng.integers(2, 16, count), repair.CONTEXT, n)


def residuals(x: np.ndarray, starts: np.ndarray, ends: np.ndarray) -> np.ndarray:
    y, _ = repair.repair(x, starts, ends, device=torch.device("cpu"))
    return x - y


def extract(x: np.ndarray, rate: int, rng: np.random.Generator) -> list[np.ndarray]:
    """Click waveforms from one channel, normalised to unit peak."""
    starts, ends = candidate_spans(highpass(x, rate), rate, x.size)
    if starts.size == 0:
        return []
    res = residuals(x, starts, ends)

    taken = np.zeros(x.size, dtype=bool)
    for a, b in zip(starts, ends, strict=True):
        taken[max(0, a - 2 * repair.CONTEXT) : b + 2 * repair.CONTEXT] = True
    cs, ce = control_spans(x.size, taken, rng)
    if cs.size == 0:
        return []
    control = residuals(x, cs, ce)
    peaks = [np.abs(control[a:b]).max() for a, b in zip(cs, ce, strict=True)]
    floor = float(np.percentile(peaks, CONTROL_PCT))
    if not np.isfinite(floor) or floor <= 0.0:
        return []

    out = []
    for a, b in zip(starts, ends, strict=True):
        seg = res[a:b]
        peak = float(np.abs(seg).max())
        if peak < floor or peak <= 0.0:
            continue
        if max(abs(seg[0]), abs(seg[-1])) > EDGE_FRACTION * peak:
            continue  # the span stopped inside the click
        out.append((seg / peak).astype(np.float32))
        if len(out) >= MAX_CLICKS:
            break
    return out


def quiet_regions(x: np.ndarray, rate: int, quiet_db: float) -> list[tuple[int, int]]:
    """Runs at least MIN_QUIET_MS long whose RMS is ``quiet_db`` below the track median."""
    hop = max(1, int(round(FRAME_MS * 1e-3 * rate)))
    n_frames = x.size // hop
    if n_frames < 4:
        return []
    frames = x[: n_frames * hop].reshape(n_frames, hop)
    rms = np.sqrt(np.mean(frames.astype(np.float64) ** 2, axis=1))
    median = float(np.median(rms))
    if median <= DIGITAL_SILENCE:
        return []
    quiet = rms < median * 10.0 ** (-quiet_db / 20.0)
    min_frames = max(1, int(round(MIN_QUIET_MS / FRAME_MS)))
    padded = np.concatenate(([False], quiet, [False]))
    edges = np.diff(padded.astype(np.int8))
    out = []
    for s, e in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1), strict=True):
        if e - s < min_frames:
            continue
        region = x[s * hop : e * hop]
        if float(np.sqrt(np.mean(region.astype(np.float64) ** 2))) <= DIGITAL_SILENCE:
            continue  # digital silence padded onto the transfer, not a real groove
        out.append((s * hop, e * hop))
    return out


def beds(x: np.ndarray, rate: int, quiet_db: float) -> list[np.ndarray]:
    """Quarter-second stretches of groove noise with no detected click anywhere in them."""
    out: list[np.ndarray] = []
    for lo, hi in quiet_regions(x, rate, quiet_db):
        region = x[lo:hi]
        if region.size < BED_SAMPLES:
            continue
        starts, ends = candidate_spans(highpass(region, rate), rate, region.size)
        clicky = np.zeros(region.size, dtype=bool)
        for a, b in zip(starts, ends, strict=True):
            clicky[a:b] = True
        for start in range(0, region.size - BED_SAMPLES + 1, BED_SAMPLES):
            chunk = slice(start, start + BED_SAMPLES)
            seg = region[chunk].astype(np.float32)
            if clicky[chunk].any():
                continue
            if float(np.sqrt(np.mean(seg.astype(np.float64) ** 2))) <= DIGITAL_SILENCE:
                continue
            out.append(seg)
            if len(out) >= MAX_BEDS:
                return out
    return out


def harvest_one(doc: dict, out_dir: Path, work_dir: Path, quiet_db: float) -> _ia.Outcome:
    ident = doc["identifier"]
    target = out_dir / f"{ident}.npz"
    if target.exists():
        with np.load(target) as blob:
            return _ia.Outcome(ident, "ok", "cached", {"clicks": int(blob["offsets"].size - 1)})
    try:
        data, info = _ia.fetch_audio(
            ident,
            work_dir,
            whole_below=WHOLE_FILE_BYTES,
            head_bytes=HEAD_BYTES,
            rate_out=detect.ANALYSIS_RATE,
        )
        if info["rate"] < MIN_SOURCE_RATE:
            return _ia.Outcome(ident, "skip", f"source rate {info['rate']} Hz")
        rate = detect.ANALYSIS_RATE
        if data.shape[0] < 4 * rate:
            return _ia.Outcome(ident, "skip", "less than 4 s decoded")

        rng = np.random.default_rng(_ia.seed_of(ident))
        clicks: list[np.ndarray] = []
        collected: list[np.ndarray] = []
        for ch in range(min(2, data.shape[1])):
            x = np.ascontiguousarray(data[:, ch], dtype=np.float64)
            energy = float((x**2).sum())
            if energy <= 0.0:
                continue
            if float((highpass(x, rate) ** 2).sum()) / energy > MAX_HF_FRACTION:
                return _ia.Outcome(ident, "skip", "too much treble to be a 78 transfer")
            clicks.extend(extract(x, rate, rng))
            collected.extend(beds(x, rate, quiet_db))
        if not clicks:
            return _ia.Outcome(ident, "skip", "no clicks above the calibrated floor")

        clicks = clicks[:MAX_CLICKS]
        collected = collected[:MAX_BEDS]
        np.savez_compressed(
            target,
            clicks=np.concatenate(clicks).astype(np.float32),
            offsets=np.cumsum([0] + [c.size for c in clicks]).astype(np.int32),
            beds=(
                np.stack(collected).astype(np.float32)
                if collected
                else np.zeros((0, BED_SAMPLES), np.float32)
            ),
        )
        return _ia.Outcome(
            ident,
            "ok",
            f"{len(clicks)} clicks, {len(collected)} beds",
            {"clicks": len(clicks), "beds": len(collected), **info},
        )
    except Exception as exc:
        return _ia.Outcome(ident, "error", f"{type(exc).__name__}: {exc}")


def main(argv: list[str] | None = None) -> int:
    ap = _ia.build_parser(__doc__, items=400, out="corpus/noise")
    ap.add_argument("--quiet-db", type=float, default=QUIET_DB)
    args = ap.parse_args(argv)
    return _ia.harvest(
        COLLECTION, args, lambda d: harvest_one(d, args.out, args.work, args.quiet_db)
    )


if __name__ == "__main__":
    raise SystemExit(_ia.run_cli(main))
