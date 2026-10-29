"""Reject corrupt evaluation evidence and preserve outputs when a quality gate fails."""

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

import metrics
import mix
import train
from grooveclean import detect


def artifact(tmp_path, **changes):
    stem = tmp_path / "eval"
    sf.write(stem.with_suffix(".flac"), np.zeros(200), 44100)
    values = dict(bounds=np.array([0, 100, 200]), kind=np.array([1, 0], dtype=np.int8),
                  mask=np.packbits(np.r_[np.ones(10), np.zeros(190)].astype(bool)), rate=44100)
    values.update(changes)
    np.savez(stem.with_suffix(".npz"), **values)
    return stem


@pytest.mark.parametrize("changes", [
    {"bounds": np.array([0, 200, 100])},
    {"bounds": np.array([1, 100, 200])},
    {"bounds": np.array([0, 100, 199])},
    {"bounds": np.array([0, 0, 200])},
    {"bounds": np.array([0., 100., 200.])},
    {"kind": np.array([1])},
    {"kind": np.array([1, 2])},
    {"kind": np.array([[1, 0]])},
    {"mask": np.zeros(1, dtype=np.uint8)},
    {"mask": np.zeros(25, dtype=np.float32)},
    {"mask": np.packbits(np.ones(200, dtype=bool))},
    {"rate": 48000},
])
def test_loader_rejects_malformed_evidence(tmp_path, changes):
    with pytest.raises(mix.CorpusError):
        mix.load_eval(artifact(tmp_path, **changes))


def test_loader_accepts_the_complete_artifact(tmp_path):
    segments, masks, kinds, rate = mix.load_eval(artifact(tmp_path))
    assert [len(a) for a in segments] == [100, 100]
    assert [int(m.sum()) for m in masks] == [10, 0]
    assert list(kinds) == [1, 0]
    assert rate == 44100


@pytest.mark.parametrize("contents", [b"", b"not a numpy archive"])
def test_loader_reports_unreadable_metadata(tmp_path, contents):
    stem = artifact(tmp_path)
    stem.with_suffix(".npz").write_bytes(contents)
    with pytest.raises(mix.CorpusError, match="cannot read evaluation artifact"):
        mix.load_eval(stem)


@pytest.mark.parametrize("suffix", [".flac", ".npz"])
def test_partial_calibration_cache_is_not_overwritten(tmp_path, suffix, monkeypatch):
    stem = tmp_path / "partial"
    cached = stem.with_suffix(suffix)
    cached.write_bytes(b"preserve me")
    def unexpected(*args):
        pytest.fail("incomplete cached artifact was overwritten")
    monkeypatch.setattr(mix, "write_eval", unexpected)
    with pytest.raises(mix.CorpusError, match="incomplete"):
        train.validation_set(None, 1, stem, Path("unused"))
    assert cached.read_bytes() == b"preserve me"


@pytest.mark.parametrize("failed", ["calibration", "test", "missing_truth", "missing_clean",
                                    "short_clean", "clean_fp", "pass"])
def test_failed_training_gates_preserve_existing_checkpoint(tmp_path, monkeypatch, failed):
    good = metrics.Score(tp=100, clean_seconds=200)
    bad = metrics.Score(tp=1, fn=99, clean_seconds=200)
    calibration = bad if failed == "calibration" else good
    final = {"missing_truth": metrics.Score(clean_seconds=200),
             "missing_clean": metrics.Score(tp=100),
             "short_clean": metrics.Score(tp=100, clean_seconds=1),
             "clean_fp": metrics.Score(tp=100, clean_seconds=200, clean_fp=4),
             }.get(failed, bad if failed == "test" else good)
    corpus = mix.Corpus([np.ones(3)], np.zeros((0, 1)), [Path("unused")])
    stem = artifact(tmp_path)
    evaluation = mix.load_eval(stem)
    monkeypatch.setattr(mix, "load_corpus", lambda *args: corpus)
    monkeypatch.setattr(train, "validation_set", lambda *args: evaluation)
    monkeypatch.setattr(train, "check_sources", lambda *args, **kwargs: True)
    monkeypatch.setattr(train, "DataLoader", lambda *args, **kwargs: [])
    factory = detect.ClickCNN
    model = factory(channels=2, blocks=1, kernel=3)
    monkeypatch.setattr(detect, "ClickCNN", lambda **config: factory(**config) if config else model)
    monkeypatch.setattr(train, "calibrate", lambda *args: (.95, .55, calibration))
    monkeypatch.setattr(metrics, "probabilities", lambda *args: [])
    monkeypatch.setattr(metrics, "active_masks", lambda *args: [])
    monkeypatch.setattr(metrics, "evaluate", lambda *args: final)
    out = tmp_path / "detector.pt"
    out.write_bytes(b"existing weights")
    out.with_suffix(".json").write_bytes(b"existing metadata")
    result = train.main(["--steps", "1", "--workers", "0", "--device", "cpu", "--out", str(out),
                         "--eval", str(stem), "--calibration", str(tmp_path / "calibration")])
    if failed == "pass":
        assert result == 0
        assert detect.Detector.load(out, device="cpu").calibration.hi == .95
    else:
        assert result == 1
        assert out.read_bytes() == b"existing weights"
        assert out.with_suffix(".json").read_bytes() == b"existing metadata"
