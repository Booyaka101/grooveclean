"""Least-squares AR interpolation of click spans, batched across a whole channel.

For each gap an order-64 AR model is fitted to the surrounding audio and the missing samples
are chosen to minimise the model's prediction error over every window that touches the gap.
This is the interpolator GTK Wave Cleaner calls LSAR; the difference here is that the normal
equations for every span in the channel are assembled and solved as one batched tensor, so a
side with forty thousand clicks costs one kernel launch per size bucket instead of forty
thousand solves.

The same code runs on CUDA and on CPU tensors; ``device`` only selects where.
"""

from __future__ import annotations

import numpy as np
import torch

ORDER = 64
CONTEXT = 4 * ORDER  # samples of clean audio needed either side to fit the model
RIDGE = 1e-9
LAG_WINDOW = 1.0001  # white-noise correction on r[0], keeps the Toeplitz system conditioned

LSAR, CUBIC, UNREPAIRED = 0, 1, 2
METHOD_NAMES = ("lsar", "cubic", "unrepaired")

_GPU_SOLVE_ELEMS = 32_000_000
_CPU_SOLVE_ELEMS = 4_000_000


def repair(
    x: np.ndarray,
    starts: np.ndarray,
    ends: np.ndarray,
    *,
    device: torch.device,
    order: int = ORDER,
    force_cubic: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (repaired copy of ``x``, per-span method code).

    ``starts``/``ends`` must be sorted and non-overlapping. Spans without ``CONTEXT`` samples
    of room either side, or flagged in ``force_cubic``, are filled by cubic interpolation
    instead and reported as such.
    """
    y = np.array(x, dtype=np.float64, copy=True)
    methods = np.full(starts.size, LSAR, dtype=np.int8)
    if starts.size == 0:
        return y, methods

    context = 4 * order
    short = (starts < context) | (ends > x.size - context)
    if force_cubic is not None:
        short = short | force_cubic
    methods[short] = CUBIC

    filled = _bridge_gaps(x, starts, ends)
    for idx in np.flatnonzero(short):
        y[starts[idx] : ends[idx]] = _cubic_gap(filled, int(starts[idx]), int(ends[idx]))

    keep = np.flatnonzero(~short)
    if keep.size:
        _lsar_batched(filled, starts[keep], ends[keep], y, device=device, order=order)
    return y, methods


def _bridge_gaps(x: np.ndarray, starts: np.ndarray, ends: np.ndarray) -> np.ndarray:
    """Linearly bridge every span, giving each fit a context free of its neighbours' clicks.

    In dense crackle the 256-sample context around one click routinely contains several more.
    Leaving them in biases the autocorrelation towards the clicks themselves.
    """
    filled = np.array(x, dtype=np.float64, copy=True)
    gap = np.zeros(x.size + 1, dtype=np.int8)
    np.add.at(gap, starts, 1)
    np.add.at(gap, ends, -1)
    inside = np.cumsum(gap[:-1]) > 0
    if not inside.any():
        return filled
    known = np.flatnonzero(~inside)
    if known.size < 2:
        return filled
    todo = np.flatnonzero(inside)
    filled[todo] = np.interp(todo, known, x[known])
    return filled


def _cubic_gap(x: np.ndarray, start: int, end: int) -> np.ndarray:
    """Catmull-Rom through the two samples either side, degrading gracefully at the array edge."""
    n = x.size
    left = [x[i] for i in (start - 2, start - 1) if 0 <= i < n]
    right = [x[i] for i in (end, end + 1) if 0 <= i < n]
    if not left and not right:
        return np.zeros(end - start, dtype=np.float64)
    if not left:
        left = [right[0], right[0]]
    if not right:
        right = [left[-1], left[-1]]
    if len(left) == 1:
        left = [left[0], left[0]]
    if len(right) == 1:
        right = [right[0], right[0]]
    p0, p1, p2, p3 = left[0], left[1], right[0], right[1]
    t = (np.arange(end - start, dtype=np.float64) + 1.0) / (end - start + 1)
    t2, t3 = t * t, t * t * t
    return 0.5 * (
        (2 * p1)
        + (-p0 + p2) * t
        + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
        + (-p0 + 3 * p1 - 3 * p2 + p3) * t3
    )


def _levinson(r: torch.Tensor) -> torch.Tensor:
    """Batched Levinson-Durbin. ``r`` is [B, order+1]; returns [B, order] predictor coefficients."""
    batch, order = r.shape[0], r.shape[1] - 1
    a = torch.zeros(batch, order, dtype=r.dtype, device=r.device)
    err = r[:, 0].clone()
    for i in range(order):
        acc = r[:, i + 1]
        if i:
            acc = acc - (a[:, :i] * r[:, 1 : i + 1].flip(-1)).sum(-1)
        # Clamping the reflection coefficient keeps the fitted model minimum-phase even when
        # the context is degenerate (digital silence, a DC block, a fade to nothing).
        k = (acc / err.clamp_min(1e-30)).clamp(-0.999, 0.999)
        nxt = torch.zeros_like(a)
        if i:
            nxt[:, :i] = a[:, :i] - k[:, None] * a[:, :i].flip(-1)
        nxt[:, i] = k
        a = nxt
        err = err * (1.0 - k * k)
    return a


def _autocorr(seg: torch.Tensor, order: int) -> torch.Tensor:
    n_fft = 1 << int(np.ceil(np.log2(2 * seg.shape[-1])))
    spec = torch.fft.rfft(seg, n=n_fft, dim=-1)
    return torch.fft.irfft(spec.real**2 + spec.imag**2, n=n_fft, dim=-1)[..., : order + 1]


def _lsar_batched(
    source: np.ndarray,
    starts: np.ndarray,
    ends: np.ndarray,
    out: np.ndarray,
    *,
    device: torch.device,
    order: int,
) -> None:
    context = 4 * order
    by_width = np.argsort(ends - starts, kind="stable")
    starts, ends = starts[by_width], ends[by_width]
    widths = (ends - starts).astype(np.int64)
    budget = _GPU_SOLVE_ELEMS if device.type == "cuda" else _CPU_SOLVE_ELEMS
    signal = torch.from_numpy(source).to(device, torch.float32)

    for lo, hi in _buckets(widths, budget):
        sel = slice(lo, hi)
        gmax = int(widths[sel].max())
        heads = torch.from_numpy(starts[sel]).to(device)
        block = _gather(signal, heads, gmax + 2 * context, context)
        width = torch.from_numpy(widths[sel]).to(device)
        pos = torch.arange(block.shape[1], device=device)[None, :]
        in_gap = (pos >= context) & (pos < context + width[:, None])

        before = block[:, :context]
        after = torch.gather(
            block, 1, context + width[:, None] + torch.arange(context, device=device)[None, :]
        )
        r = _autocorr(before, order) + _autocorr(after, order)
        r[:, 0] = r[:, 0] * LAG_WINDOW + RIDGE
        coeffs = torch.cat([torch.ones_like(r[:, :1]), -_levinson(r)], dim=1)

        # Flipped kernel because this is the forward filter e[n] = sum_m b_m z[n-m]; the
        # normal-equation right-hand side below correlates the other way and wants it unflipped.
        zeroed = torch.where(in_gap, torch.zeros_like(block), block)
        residual = _grouped(zeroed, coeffs.flip(-1))
        residual = residual[:, context - order : context + gmax]
        rhs = -_grouped(residual, coeffs)

        auto = torch.stack(
            [(coeffs[:, : order + 1 - m] * coeffs[:, m:]).sum(-1) for m in range(order + 1)], dim=1
        )
        lag = (pos[:, :gmax, None] - pos[:, None, :gmax]).abs()
        normal = torch.cat([auto, torch.zeros_like(auto[:, :1])], dim=1)[
            :, lag.clamp(max=order + 1)[0]
        ]
        normal = _pad_identity(normal, width, gmax)
        rhs = torch.where(pos[:, :gmax] < width[:, None], rhs, torch.zeros_like(rhs))

        try:
            fill = torch.linalg.solve(normal.double(), rhs.double()[..., None])[..., 0]
        except RuntimeError:
            fill = torch.linalg.lstsq(normal.double(), rhs.double()[..., None]).solution[..., 0]
        fill = fill.float().cpu().numpy()
        for i, span in enumerate(range(lo, hi)):
            out[starts[span] : ends[span]] = fill[i, : widths[span]]


def _buckets(widths: np.ndarray, budget: int) -> list[tuple[int, int]]:
    """Contiguous runs of the width-sorted spans whose padded solve fits the memory budget.

    ``widths`` arrives sorted, so each run wastes at most (max-min) padding per span.
    """
    out, lo = [], 0
    for i in range(widths.size):
        gmax = int(widths[i])
        if (i + 1 - lo) * gmax * gmax > budget and i > lo:
            out.append((lo, i))
            lo = i
    out.append((lo, widths.size))
    return out


def _gather(signal: torch.Tensor, starts: torch.Tensor, length: int, context: int) -> torch.Tensor:
    idx = starts[:, None] - context + torch.arange(length, device=signal.device)[None, :]
    return signal[idx.clamp(0, signal.numel() - 1)]


def _grouped(x: torch.Tensor, kernel: torch.Tensor) -> torch.Tensor:
    """Per-row FIR: out[b, i] = sum_m kernel[b, m] * x[b, i + m]."""
    batch = x.shape[0]
    return torch.nn.functional.conv1d(x[None], kernel[:, None, :], groups=batch)[0]


def _pad_identity(normal: torch.Tensor, width: torch.Tensor, gmax: int) -> torch.Tensor:
    """Neutralise the padded rows/columns of short spans so the batched solve returns zeros."""
    pos = torch.arange(gmax, device=normal.device)
    live = pos[None, :] < width[:, None]
    normal = normal * (live[:, :, None] & live[:, None, :])
    eye = torch.eye(gmax, device=normal.device, dtype=normal.dtype)
    return normal + eye[None] * (~live)[:, :, None]
