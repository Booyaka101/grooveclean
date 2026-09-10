"""The interpolator, against an independent reference.

repair.py solves every span in a channel as one batched tensor. The reference below builds the
prediction-error design matrix for a single span and hands it to numpy's least squares, which
is the textbook statement of the same problem and shares no code with the shipped version.
It lives here rather than in the package so what ships has exactly one implementation.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from grooveclean import repair

ORDER = repair.ORDER
CONTEXT = repair.CONTEXT
DEVICES = ["cpu"] + (["cuda"] if torch.cuda.is_available() else [])


def autocorrelation(x: np.ndarray, order: int) -> np.ndarray:
    return np.array(
        [float(x[m:] @ x[: x.size - m]) if m else float(x @ x) for m in range(order + 1)]
    )


def predictor(before: np.ndarray, after: np.ndarray, order: int) -> np.ndarray:
    """Yule-Walker solved directly, rather than by the Levinson recursion repair.py uses."""
    r = autocorrelation(before, order) + autocorrelation(after, order)
    r[0] = r[0] * repair.LAG_WINDOW + repair.RIDGE
    lag = np.abs(np.subtract.outer(np.arange(order), np.arange(order)))
    return np.linalg.solve(r[lag], r[1 : order + 1])


def lsar_reference(x: np.ndarray, start: int, end: int, order: int = ORDER) -> np.ndarray:
    """Least-squares AR fill for one gap, via the explicit prediction-error matrix."""
    context = 4 * order
    seg = x[start - context : end + context].astype(np.float64)
    coeffs = predictor(x[start - context : start], x[end : end + context], order)
    b = np.concatenate([[1.0], -coeffs])

    n, width = seg.size, end - start
    rows = n - order
    design = np.zeros((rows, n))
    for i in range(rows):
        design[i, i : i + order + 1] = b[::-1]

    gap = np.arange(context, context + width)
    known = seg.copy()
    known[gap] = 0.0
    solution, *_ = np.linalg.lstsq(design[:, gap], -design @ known, rcond=None)
    return solution


def ar_signal(n: int, rng: np.random.Generator, order: int = 4) -> np.ndarray:
    """A stable AR process, so an AR interpolator has something real to recover."""
    coeffs = np.array([1.6, -1.2, 0.55, -0.15])[:order]
    x = rng.normal(0.0, 1.0, n)
    for i in range(order, n):
        x[i] += coeffs @ x[i - order : i][::-1]
    return x / np.abs(x).max()


@pytest.mark.parametrize("device", DEVICES)
@pytest.mark.parametrize("width", [1, 3, 12, 40])
def test_batched_lsar_matches_the_reference(device, width):
    rng = np.random.default_rng(11)
    x = ar_signal(6000, rng)
    starts = np.array([1000, 2500, 4200], dtype=np.int64)
    ends = starts + width

    y, methods = repair.repair(x, starts, ends, device=torch.device(device))
    assert (methods == repair.LSAR).all()
    scale = float(np.sqrt(np.mean(x**2)))
    for start, end in zip(starts, ends, strict=True):
        assert np.abs(y[start:end] - lsar_reference(x, int(start), int(end))).max() < 1e-3 * scale


@pytest.mark.parametrize("device", DEVICES)
def test_only_the_gaps_move(device):
    rng = np.random.default_rng(12)
    x = ar_signal(4000, rng)
    starts = np.array([500, 1500, 3000], dtype=np.int64)
    ends = starts + np.array([2, 9, 30])

    y, _ = repair.repair(x, starts, ends, device=torch.device(device))
    keep = np.ones(x.size, dtype=bool)
    for start, end in zip(starts, ends, strict=True):
        keep[start:end] = False
    assert np.array_equal(y[keep], x[keep])
    assert not np.array_equal(y[~keep], x[~keep])


def test_the_fill_is_quieter_than_the_click_it_replaces():
    rng = np.random.default_rng(13)
    x = ar_signal(4000, rng)
    damaged = x.copy()
    damaged[2000:2006] += 8.0
    y, _ = repair.repair(damaged, np.array([2000]), np.array([2006]), device=torch.device("cpu"))
    gap = slice(2000, 2006)
    assert np.abs(y[gap] - x[gap]).max() < np.abs(damaged[gap] - x[gap]).max()


def test_spans_at_the_edges_fall_back_to_cubic():
    rng = np.random.default_rng(14)
    x = ar_signal(2000, rng)
    starts = np.array([10, 900, 1990], dtype=np.int64)
    ends = np.array([14, 906, 1996], dtype=np.int64)

    y, methods = repair.repair(x, starts, ends, device=torch.device("cpu"))
    assert list(methods) == [repair.CUBIC, repair.LSAR, repair.CUBIC]
    assert np.isfinite(y).all()


def test_force_cubic_is_honoured():
    rng = np.random.default_rng(15)
    x = ar_signal(2000, rng)
    starts, ends = np.array([700, 1200]), np.array([706, 1206])
    _, methods = repair.repair(
        x, starts, ends, device=torch.device("cpu"), force_cubic=np.array([True, False])
    )
    assert list(methods) == [repair.CUBIC, repair.LSAR]


@pytest.mark.parametrize(
    "make",
    [
        pytest.param(lambda n: np.zeros(n), id="digital_silence"),
        pytest.param(lambda n: np.full(n, 0.4), id="dc_block"),
        pytest.param(lambda n: np.sign(np.sin(np.arange(n) * 0.01)) * 0.9, id="hard_square"),
        pytest.param(lambda n: np.linspace(-1.0, 1.0, n), id="ramp"),
    ],
)
def test_degenerate_context_stays_finite(make):
    x = make(4000)
    starts = np.array([1000, 2000, 3000], dtype=np.int64)
    y, _ = repair.repair(x, starts, starts + 5, device=torch.device("cpu"))
    assert np.isfinite(y).all()
    assert np.abs(y).max() <= np.abs(x).max() + 1.0


def test_no_spans_is_a_copy():
    x = ar_signal(500, np.random.default_rng(16))
    y, methods = repair.repair(
        x, np.zeros(0, np.int64), np.zeros(0, np.int64), device=torch.device("cpu")
    )
    assert np.array_equal(y, x) and methods.size == 0


@pytest.mark.parametrize("device", DEVICES)
def test_many_spans_of_mixed_width(device):
    """The size buckets are the part most likely to mis-index; give them plenty to sort.

    Spans are spaced further apart than the fitting context, so each one is the only damage
    its own model sees and the single-span reference still applies.
    """
    rng = np.random.default_rng(17)
    x = ar_signal(200_000, rng)
    starts = np.arange(400, 199_000, 600, dtype=np.int64)
    ends = starts + rng.integers(1, 45, starts.size)

    y, methods = repair.repair(x, starts, ends, device=torch.device(device))
    assert np.isfinite(y).all()
    assert (methods == repair.LSAR).all()
    assert starts.size > 300
    for pick in (0, 137, starts.size - 1):
        reference = lsar_reference(x, int(starts[pick]), int(ends[pick]))
        assert np.abs(y[starts[pick] : ends[pick]] - reference).max() < 1e-3 * np.abs(x).max()


@pytest.mark.parametrize("device", DEVICES)
def test_dense_crackle_does_not_poison_its_own_context(device):
    """With a click every 60 samples the fitting context is full of other clicks.

    They are bridged before the fit, so the result has to stay bounded by the music rather
    than tracking the damage. There is no closed-form reference for this case.
    """
    rng = np.random.default_rng(18)
    x = ar_signal(60_000, rng)
    starts = np.arange(400, 59_000, 60, dtype=np.int64)
    damaged = x.copy()
    for start in starts:
        damaged[start : start + 6] += rng.uniform(-6.0, 6.0)

    y, _ = repair.repair(damaged, starts, starts + 6, device=torch.device(device))
    assert np.isfinite(y).all()
    assert np.abs(y).max() < 3.0 * np.abs(x).max()
    inside = np.zeros(x.size, dtype=bool)
    for start in starts:
        inside[start : start + 6] = True
    assert np.abs(y[inside] - x[inside]).mean() < np.abs(damaged[inside] - x[inside]).mean()
