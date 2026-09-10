"""Group 3: detector F1 on held-out synthetic mixes, and its false positive rate on music.

The evaluation set is built by train/mix.py from the 10% of source items that training never
saw, on either side of the mix. Both numbers are hard gates: the brief asks for F1 at or above
0.95 with no more than one false positive per minute of click-free music, and a detector that
misses either of those is not shippable.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

import metrics
import mix
from conftest import DATA
from grooveclean import detect

MIN_F1 = 0.95
MAX_FP_PER_MINUTE = 1.0


@pytest.fixture(scope="module")
def held_out():
    stem = DATA / "detector_eval"
    if not stem.with_suffix(".flac").exists():
        pytest.skip(f"{stem}.flac is missing; run python train/mix.py --split test")
    return mix.load_eval(stem)


@pytest.fixture(scope="module")
def scored(held_out, detector) -> metrics.Score:
    segments, masks, kinds, rate = held_out
    gate = detect.thresholds(0.5, 0.5, 0.5)[2]
    return metrics.evaluate(
        metrics.probabilities(detector, segments, rate),
        metrics.active_masks(segments, rate, gate),
        masks,
        kinds,
        rate,
        detector.calibration.hi,
        detector.calibration.lo,
    )


def test_the_evaluation_set_is_worth_scoring(held_out):
    segments, masks, kinds, rate = held_out
    assert rate == detect.ANALYSIS_RATE
    assert len(segments) == len(masks) == len(kinds)
    assert int((kinds == 1).sum()) >= 20 and int((kinds == 0).sum()) >= 20
    clicky = sum(int(m.sum()) for m, k in zip(masks, kinds, strict=True) if k)
    assert clicky > 0
    assert all(not m.any() for m, k in zip(masks, kinds, strict=True) if not k)
    clean_seconds = sum(m.size for m, k in zip(masks, kinds, strict=True) if not k) / rate
    assert clean_seconds >= 180.0, clean_seconds


def test_f1_meets_the_bar(scored):
    assert scored.f1 >= MIN_F1, str(scored)


def test_false_positives_on_clean_music_stay_under_budget(scored):
    assert scored.fp_per_minute <= MAX_FP_PER_MINUTE, str(scored)


def test_sensitivity_moves_the_detector_in_the_right_direction(held_out, detector):
    """Turning the knob up has to find more, not fewer. It is the only control a user has."""
    segments, masks, kinds, rate = held_out
    clicky = [seg for seg, kind in zip(segments, kinds, strict=True) if kind][:12]
    probs = metrics.probabilities(detector, clicky, rate)
    # Samples, not spans: turning the knob up widens spans until neighbours merge, so the
    # span count can fall while strictly more of the record is being repaired.
    found = []
    for sensitivity in (0.2, 0.5, 0.8):
        hi, lo, gate = detect.thresholds(
            sensitivity, detector.calibration.hi, detector.calibration.lo
        )
        actives = metrics.active_masks(clicky, rate, gate)
        repaired = 0
        for p, a in zip(probs, actives, strict=True):
            starts, ends, _ = detect.spans(p, a, rate, hi, lo)
            repaired += int((ends - starts).sum())
        found.append(repaired)
    assert found[0] <= found[1] <= found[2], found
    assert found[0] < found[2]


def test_probabilities_do_not_depend_on_the_chunk_boundary(held_out, detector, monkeypatch):
    """Inference is chunked; a click must score the same wherever the chunk edges land."""
    segments, _, kinds, rate = held_out
    segment = next(seg for seg, kind in zip(segments, kinds, strict=True) if kind)
    x = torch.from_numpy(segment[None, :].astype(np.float32))
    whole = detector.probabilities(x, rate).cpu().numpy()
    monkeypatch.setattr(detect, "INFER_CHUNK", 4096)
    chunked = detector.probabilities(x, rate).cpu().numpy()
    assert np.abs(whole - chunked).max() < 1e-3
