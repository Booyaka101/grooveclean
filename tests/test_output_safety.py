"""Output aliases must be rejected before any member of an input set is changed."""

import json
import os
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from grooveclean import cli, io, review


@pytest.fixture
def pair(tmp_path):
    cleaned = tmp_path / "clean.wav"
    removed, report = io.sidecars(cleaned)
    for path in (cleaned, removed):
        sf.write(path, np.zeros(1000), 44100, subtype="PCM_16")
    report.write_text(json.dumps({"sample_rate": 44100, "clicks": [{
        "channel": 0, "start_sample": 100, "end_sample": 110, "width_samples": 10,
        "confidence": .9, "residual_rms": .01, "repair": "cubic",
    }]}), encoding="utf-8")
    return review.open_pair(cleaned)


@pytest.mark.parametrize("operation", ["clean", "audit", "revert"])
@pytest.mark.parametrize("target", ["cleaned", "removed", "report"])
def test_hardlinked_outputs_preserve_inputs(pair, tmp_path, operation, target):
    source = Path(pair.cleaned.path)
    inputs = (source, *io.sidecars(source))
    original = [path.read_bytes() for path in inputs]
    alias = tmp_path / "alias.wav"
    index = {"cleaned": 0, "removed": 1, "report": 2}[target]
    if operation == "clean":
        os.link(source, (alias, *io.sidecars(alias))[index])
    else:
        os.link(inputs[index], alias)
    with pytest.raises(io.AudioError, match="choose another -o"):
        if operation == "clean":
            cli.clean_file(source, alias, detector=None)
        elif operation == "audit":
            review.audit(pair, [0], alias, tmp_path / "after.wav", 1)
        else:
            review.revert(pair, [0], alias)
    assert [path.read_bytes() for path in inputs] == original


@pytest.mark.parametrize("operation", ["audit", "revert"])
def test_direct_review_rejects_input_path(pair, tmp_path, operation):
    source = Path(pair.cleaned.path)
    original = source.read_bytes()
    with pytest.raises(io.AudioError, match="choose another -o"):
        if operation == "audit":
            review.audit(pair, [0], source, tmp_path / "after.wav", 1)
        else:
            review.revert(pair, [0], source)
    assert source.read_bytes() == original


def test_audit_rejects_aliased_output_pair(pair, tmp_path):
    before = tmp_path / "before.wav"
    before.write_bytes(b"keep")
    after = tmp_path / "after.wav"
    os.link(before, after)
    with pytest.raises(io.AudioError, match="choose another -o"):
        review.audit(pair, [0], before, after, 1)
    assert before.read_bytes() == b"keep"


@pytest.mark.parametrize("changes", [
    {"width_samples": "10"}, {"width_samples": 11}, {"width_samples": True},
    {"confidence": "high"}, {"confidence": float("nan")}, {"confidence": 1.1},
    {"confidence": True}, {"residual_rms": -1}, {"residual_rms": float("inf")},
    {"residual_rms": []}, {"repair": "guess"}, {"repair": []}, {"channel": False},
])
def test_malformed_report_fields_are_rejected_at_load(pair, changes):
    path = io.sidecars(Path(pair.cleaned.path))[1]
    built = pair.report
    built["clicks"][0].update(changes)
    path.write_text(json.dumps(built), encoding="utf-8")
    with pytest.raises(review.ReviewError):
        review.open_pair(pair.cleaned.path)


@pytest.mark.parametrize("text", ["nan", "inf", "-inf", "1:nan", "-2"])
def test_nonfinite_or_negative_review_time_is_rejected(text):
    with pytest.raises(review.ReviewError):
        review.parse_time(text)
