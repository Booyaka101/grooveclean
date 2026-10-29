"""Independent analytical and set-based checks, without tuning model thresholds."""

import numpy as np
import pytest
import torch

import metrics
from grooveclean import detect


@pytest.mark.parametrize("n_in", [15, 16, 31, 32])
@pytest.mark.parametrize("n_out", [9, 10, 45, 46])
def test_resampling_preserves_analytic_low_frequency_tones(n_in, n_out):
    def wave(n):
        t = np.arange(n) / n
        return .2 + .3 * np.cos(2 * np.pi * t) + .1 * np.sin(4 * np.pi * t)
    x = torch.from_numpy(wave(n_in).astype(np.float32))
    np.testing.assert_allclose(detect.resample(x, n_out).numpy(), wave(n_out), atol=2e-7)


@pytest.mark.parametrize("n_in,n_out", [(16, 32), (32, 16), (15, 10), (16, 31)])
def test_resampling_handles_unpaired_nyquist_bins(n_in, n_out):
    frequency = min(n_in, n_out) // 2
    x = np.cos(2 * np.pi * frequency * np.arange(n_in) / n_in)
    expected = np.cos(2 * np.pi * frequency * np.arange(n_out) / n_out)
    actual = detect.resample(torch.from_numpy(x.astype(np.float32)), n_out).numpy()
    np.testing.assert_allclose(actual, expected, atol=3e-7)


@pytest.mark.parametrize("seed", [13, 29, 47])
def test_span_merging_matches_a_simple_interval_union(seed):
    rng = np.random.default_rng(seed)
    starts = np.sort(rng.integers(0, 1000, 200))
    ends = starts + rng.integers(1, 100, starts.size)
    expected = []
    for i, (start, end) in enumerate(zip(starts, ends, strict=True)):
        if expected and start <= expected[-1][1]:
            expected[-1][1] = max(expected[-1][1], end)
        else:
            expected.append([start, end, i])
    for actual, want in zip(detect.merge_spans(starts, ends), np.array(expected).T, strict=True):
        np.testing.assert_array_equal(actual, want)


@pytest.mark.parametrize("rate", [22050, 44100, 48000, 192000])
def test_support_only_removes_events_and_sensitivity_preserves_coverage(rate):
    rng = np.random.default_rng(20261031)
    x = rng.normal(0, .01, rate).astype(np.float32)
    x[rate // 2] += .5
    p = rng.uniform(size=44100).astype(np.float32)
    p[22050] = 1
    previous = np.zeros(rate, dtype=bool)
    for sensitivity in (0, .2, .5, .8, 1):
        hi, lo, gate = detect.thresholds(sensitivity, .95, .55)
        a = detect.activity(x, rate, gate)
        old = detect.spans(p, a.mask, rate, hi, lo)
        new = detect.spans(p, a.mask, rate, hi, lo, support=a.support)
        legacy = metrics.covered(old[0], old[1], rate)
        current = metrics.covered(new[0], new[1], rate)
        assert not (current & ~legacy).any()
        assert not (previous & ~current).any()
        assert np.all(new[0] < new[1])
        assert np.all(new[0][1:] > new[1][:-1])
        previous = current
