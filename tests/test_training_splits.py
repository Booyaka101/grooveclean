"""Calibration cannot select thresholds on the final test sources or cached test audio."""

import hashlib
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

import _ia
import mix
import train


def identifiers(split):
    return [f"source-{i}" for i in range(500) if _ia.split_of(f"source-{i}") == split]


def test_three_source_splits_are_disjoint_and_preserve_the_old_test_bucket():
    groups = {name: set(identifiers(name)) for name in ("train", "calibration", "test")}
    assert all(groups.values())
    assert len(set.union(*groups.values())) == 500
    for source in set.union(*groups.values()):
        historical_test = hashlib.sha1(source.encode()).digest()[0] % 10 == 0
        assert (source in groups["test"]) == historical_test


def test_loader_rejects_unknown_split(tmp_path):
    with pytest.raises(mix.CorpusError, match="unknown corpus split"):
        mix.load_corpus(tmp_path, tmp_path, "typo")


@pytest.mark.parametrize("split,out", [("test", "tests/data/detector_eval"),
                                      ("calibration", "corpus/calibration_eval"),
                                      ("train", "corpus/train_eval")])
def test_mixer_defaults_cannot_overwrite_another_splits_artifact(monkeypatch, split, out):
    corpus = mix.Corpus([np.ones(3)], np.zeros((0, 1)), [Path("unused")])
    monkeypatch.setattr(mix, "load_corpus", lambda *args: corpus)
    written = []
    monkeypatch.setattr(mix, "write_eval", lambda *args: written.append(args[4]))
    assert mix.main(["--split", split]) == 0
    assert written == [Path(out)]


@pytest.mark.parametrize("split", ["train", "test"])
def test_calibration_refuses_cached_audio_from_another_split(tmp_path, split):
    stem = tmp_path / "calibration"
    stem.with_suffix(".flac").touch()
    sources = np.array(identifiers(split)[:2])
    np.savez(stem.with_suffix(".npz"), clean_sources=sources, noise_sources=sources)
    with pytest.raises(mix.CorpusError, match="non-calibration sources"):
        train.validation_set(None, 1, stem, Path("unused"))


def test_calibration_refuses_legacy_audio_without_source_provenance(tmp_path):
    stem = tmp_path / "legacy"
    stem.with_suffix(".flac").touch()
    np.savez(stem.with_suffix(".npz"), rate=44100)
    with pytest.raises(mix.CorpusError, match="missing clean_sources"):
        train.validation_set(None, 1, stem, Path("unused"))


@pytest.mark.parametrize("suffix", ["", ".flac", ".npz"])
def test_calibration_and_test_cannot_alias_the_same_artifact(tmp_path, suffix):
    stem = str(tmp_path / "eval")
    with pytest.raises(SystemExit) as exc:
        train.main(["--calibration", stem, "--eval", stem + suffix])
    assert exc.value.code == 2


def test_final_test_refuses_a_calibration_manifest(tmp_path):
    stem = tmp_path / "eval"
    sources = np.array(identifiers("calibration")[:2])
    np.savez(stem.with_suffix(".npz"), clean_sources=sources, noise_sources=sources)
    with pytest.raises(mix.CorpusError, match="test contains non-test"):
        train.check_sources(stem, "test", allow_legacy=True)


def test_legacy_test_provenance_is_not_falsely_certified(tmp_path):
    stem = tmp_path / "eval"
    np.savez(stem.with_suffix(".npz"), rate=44100)
    assert not train.check_sources(stem, "test", allow_legacy=True)


def test_loader_and_eval_writer_preserve_source_provenance(tmp_path, monkeypatch):
    for split in ("train", "calibration", "test"):
        source = identifiers(split)[0]
        sf.write(tmp_path / f"{source}.flac", np.zeros(100), 44100)
        np.savez(tmp_path / f"{source}.npz", offsets=[0, 3],
                 clicks=np.ones(3, dtype=np.float32),
                 beds=np.zeros((0, 44100 // 4), dtype=np.float32))
    corpus = mix.load_corpus(tmp_path, tmp_path, "calibration")
    source = identifiers("calibration")[0]
    assert corpus.noise_sources == (source,)
    assert [p.stem for p in corpus.clean] == [source]
    monkeypatch.setattr(mix, "quietest", lambda corpus: corpus)
    monkeypatch.setattr(mix, "redistributable", lambda corpus, manifest: corpus)
    monkeypatch.setattr(mix.Mixer, "draw", lambda self: (
        np.zeros((1, 100), dtype=np.float32), np.zeros((1, 100)),
        np.zeros((1, 100), dtype=bool),
    ))
    stem = tmp_path / "calibration_eval"
    mix.write_eval(corpus, 42, 1, 1, stem, tmp_path / "unused")
    assert train.check_sources(stem, "calibration")
    segments, masks, kinds, rate = mix.load_eval(stem)
    assert len(segments) == len(masks) == 2
    assert list(kinds) == [1, 0]
    assert rate == 44100
