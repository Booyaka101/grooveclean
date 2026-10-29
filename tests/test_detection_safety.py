"""Complete decisions, including stochastic controls and paired injected clicks."""

import numpy as np
import pytest
import torch

from grooveclean import detect


@pytest.mark.parametrize("size,width", [(1, 7), (2, 9), (3, 11), (8, 5)])
def test_box_mean_matches_repeated_reflection(size, width):
    x = np.arange(size, dtype=np.float32)
    padded = np.pad(x, width // 2, mode="reflect" if size > 1 else "edge")
    expected = np.convolve(padded, np.ones(width) / width, mode="valid")
    np.testing.assert_allclose(detect.box_mean(torch.from_numpy(x), width), expected)


@pytest.mark.parametrize("rate", [44100, 48000, 96000])
@pytest.mark.parametrize("size", [1, 2, 17])
def test_short_silence_is_finite_and_has_no_events(detector, rate, size):
    x = torch.zeros(2, size)
    p = detector.probabilities(x, rate)
    assert p.shape == (2, max(1, round(size * detect.ANALYSIS_RATE / rate)))
    assert torch.isfinite(p).all()
    assert all(not starts.size for starts, _, _ in detector.events(x, rate))


@pytest.mark.parametrize("shape,rate", [((10,), 44100), ((0, 10), 44100),
                                        ((1, 0), 44100), ((1, 10), 0)])
def test_public_api_rejects_empty_or_invalid_audio(detector, shape, rate):
    with pytest.raises(detect.DetectorError, match="non-empty"):
        detector.events(torch.zeros(shape), rate)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_public_api_rejects_nonfinite_samples_and_rates(detector, value):
    with pytest.raises(detect.DetectorError, match="finite"):
        detector.events(torch.full((1, 10), value), 44100)
    with pytest.raises(detect.DetectorError, match="positive rate"):
        detector.events(torch.zeros(1, 10), value)


def test_support_confirms_distributed_evidence_without_widening_spans():
    p = np.zeros(100, dtype=np.float32)
    p[20:22] = 1
    p[70] = 1
    active = p.astype(bool)
    excess = np.zeros_like(p)
    excess[20:22] = .25
    excess[70] = .1
    support = np.r_[0, np.cumsum(excess)]
    starts, ends, conf = detect.spans(p, active, 44100, .9, .5, support=support)
    np.testing.assert_array_equal(starts, [20])
    np.testing.assert_array_equal(ends, [22])
    np.testing.assert_array_equal(conf, [1])
    assert len(detect.spans(p, active, 44100, .9, .5)[0]) == 2


def test_clipping_contributes_no_support():
    x = np.zeros(1000, dtype=np.float32)
    x[490:510] = 1
    evidence = detect.activity(x, 44100, 3)
    assert not evidence.mask.any()
    assert not evidence.support.any()


@pytest.mark.parametrize("rate", [22050, 44100, 96000])
def test_support_integrates_in_analysis_rate_units(monkeypatch, rate):
    monkeypatch.setattr(detect, "impulsiveness", lambda x, r: torch.full_like(x, 4.5))
    evidence = detect.activity(np.zeros(rate, dtype=np.float32), rate, 3)
    assert evidence.support[-1] == pytest.approx(44100 * .25)


@pytest.mark.parametrize("kind", ["white", "pink"])
def test_new_noise_controls_preserve_injected_clicks(detector, kind):
    rate = 44100
    n = rate * 60
    rng = np.random.default_rng(20261030)
    clean = rng.normal(size=n)
    if kind == "pink":
        f = np.fft.rfftfreq(n, 1 / rate)
        clean = np.fft.irfft(np.fft.rfft(clean) / np.sqrt(np.maximum(f, 1)), n=n)
    clean = (clean / np.max(np.abs(clean)) * .15).astype(np.float32)
    clicked = clean.copy()
    positions = np.arange(2, 60, 5) * rate
    clicked[positions] += .65
    x = torch.from_numpy(np.stack([clean, clicked]))
    result = detector.events(x, rate)
    starts, ends, _ = result[0]
    assert len(starts) <= 1, (kind, starts, ends)
    starts, ends, _ = result[1]
    hits = [np.any((starts <= at) & (ends > at)) for at in positions]
    assert sum(hits) >= len(positions) * .95, (kind, hits)


def test_public_events_matches_cli_decision_path(detector):
    rate = 48000
    rng = np.random.default_rng(17)
    x = rng.normal(0, .005, (2, rate)).astype(np.float32)
    x[0, rate // 2] += .5
    tensor = torch.from_numpy(x)
    probs = detector.probabilities(tensor, rate).numpy()
    hi, lo, gate = detect.thresholds(.5, detector.calibration.hi, detector.calibration.lo)
    expected = [detect.click_spans(p, a, rate, hi, lo, gate)
                for p, a in zip(probs, x, strict=True)]
    actual = detector.events(tensor, rate)
    assert actual[0][0].size
    for got, want in zip(actual, expected, strict=True):
        for a, b in zip(got, want, strict=True):
            np.testing.assert_array_equal(a, b)


@pytest.mark.parametrize("rate", [22050, 48000, 96000, 192000])
def test_injected_click_is_localized_at_native_rate(detector, rate):
    reference = .05 * torch.sin(torch.arange(44100) * (2 * torch.pi * 440 / 44100))
    reference[22050] += .65
    x = detect.resample(reference[None], rate)
    starts, ends, _ = detector.events(x, rate)[0]
    assert np.any((starts <= rate // 2) & (ends > rate // 2)), (rate, starts, ends)
    assert np.all((ends - starts) / rate < .002)


def test_public_events_preserves_native_precision_for_clipping(detector, monkeypatch):
    x = torch.zeros(1, 1000, dtype=torch.float64)
    x[0, 490:493] = torch.tensor([.5, .5 - 1e-9, .5 - 2e-9], dtype=torch.float64)
    p = torch.zeros(1, 1000)
    p[0, 485:500] = 1
    monkeypatch.setattr(detector, "probabilities", lambda x, rate: p)
    hi, lo, gate = detect.thresholds(.5, detector.calibration.hi, detector.calibration.lo)
    expected = detect.click_spans(p[0].numpy(), x[0].numpy(), 44100, hi, lo, gate)
    assert expected[0].size
    actual = detector.events(x, 44100)[0]
    for got, want in zip(actual, expected, strict=True):
        np.testing.assert_array_equal(got, want)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_sensitivity_is_rejected_before_inference(detector, monkeypatch, value):
    def unexpected(*args):
        pytest.fail("invalid sensitivity reached inference")
    monkeypatch.setattr(detector, "probabilities", unexpected)
    with pytest.raises(detect.DetectorError, match="sensitivity"):
        detector.events(torch.zeros(1, 1000), 44100, value)


def test_nested_spans_merge_transitively():
    starts, ends, at = detect.merge_spans(np.array([0, 5, 10, 30]), np.array([20, 7, 15, 31]))
    np.testing.assert_array_equal(starts, [0, 30])
    np.testing.assert_array_equal(ends, [20, 31])
    np.testing.assert_array_equal(at, [0, 3])


def test_default_support_includes_an_exact_score_of_five(monkeypatch):
    def impulse(x, rate):
        result = torch.zeros_like(x)
        result[50] = 5
        return result
    monkeypatch.setattr(detect, "impulsiveness", impulse)
    a = detect.activity(np.zeros(100, dtype=np.float32), 44100, 3)
    p = np.zeros(100, dtype=np.float32)
    p[50] = 1
    assert detect.spans(p, a.mask, 44100, .9, .5, support=a.support)[0].size == 1
