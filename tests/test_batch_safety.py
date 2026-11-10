"""Batch planning must not overwrite another source or another result."""

import json
import os
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf
from click.testing import CliRunner

from grooveclean import cli, io


@pytest.fixture
def sources(tmp_path):
    directory = tmp_path / "sources"
    directory.mkdir()
    sf.write(directory / "side.wav", np.zeros(1000), 44100, subtype="PCM_16")
    return directory


def invoke(sources, destination, *options):
    return CliRunner().invoke(
        cli.main, ["batch", str(sources), "-o", str(destination), *options],
        catch_exceptions=False,
    )


@pytest.mark.parametrize("other", ["side.flac", "side.removed.wav"])
@pytest.mark.parametrize("options", [[], ["--skip-existing"], ["--dry-run"]])
def test_batch_rejects_colliding_output_names_before_loading_detector(
    sources, tmp_path, monkeypatch, other, options
):
    sf.write(sources / other, np.zeros(1000), 44100, subtype="PCM_16")
    original = {path.name: path.read_bytes() for path in sources.iterdir()}
    destination = tmp_path / "cleaned"

    def unexpected(*args, **kwargs):
        pytest.fail("output conflicts must be caught before loading the detector")

    monkeypatch.setattr(cli, "_detector", unexpected)
    result = invoke(sources, destination, *options)
    assert result.exit_code == 1
    assert "batch output conflict" in result.output
    assert "Rename conflicting sources" in result.output
    assert not destination.exists()
    assert {path.name: path.read_bytes() for path in sources.iterdir()} == original


@pytest.mark.parametrize("member", ["cleaned", "removed", "report"])
def test_batch_protects_every_source_from_output_hardlinks(sources, tmp_path, member):
    other = sources / "other.wav"
    sf.write(other, np.ones(1000) * .1, 44100, subtype="PCM_16")
    destination = tmp_path / "cleaned"
    destination.mkdir()
    target = destination / "side.wav"
    removed, report = io.sidecars(target)
    output = {"cleaned": target, "removed": removed, "report": report}[member]
    os.link(other, output)
    original = other.read_bytes()

    result = invoke(sources, destination)
    assert result.exit_code == 1
    assert "batch output conflict" in result.output
    assert other.read_bytes() == original
    assert list(destination.iterdir()) == [output]


def test_batch_protects_hardlinked_outputs_from_different_files(sources, tmp_path):
    sf.write(sources / "other.wav", np.zeros(1000), 44100, subtype="PCM_16")
    destination = tmp_path / "cleaned"
    destination.mkdir()
    target = destination / "side.wav"
    target.write_bytes(b"keep existing output")
    alias = destination / "other.removed.wav"
    os.link(target, alias)

    result = invoke(sources, destination, "--skip-existing")
    assert result.exit_code == 1
    assert "batch output conflict" in result.output
    assert target.read_bytes() == alias.read_bytes() == b"keep existing output"


@pytest.mark.parametrize("missing", ["cleaned", "removed", "both"])
def test_batch_resume_rebuilds_incomplete_audio_sets(sources, tmp_path, missing):
    destination = tmp_path / "cleaned"
    destination.mkdir()
    target = destination / "side.wav"
    removed, report = io.sidecars(target)
    report.write_text("{}", encoding="utf-8")
    if missing == "removed":
        sf.write(target, np.zeros(1000), 44100, subtype="PCM_16")
    elif missing == "cleaned":
        sf.write(removed, np.zeros(1000), 44100, subtype="PCM_16")

    result = invoke(sources, destination, "--skip-existing", "--device", "cpu")
    assert result.exit_code == 0, result.output
    assert "already done" not in result.output
    assert all(path.is_file() for path in (target, removed, report))
    assert sf.info(target).frames == 1000


def test_batch_dry_run_resumes_from_report_only(sources, tmp_path):
    destination = tmp_path / "cleaned"
    assert invoke(sources, destination, "--dry-run", "--device", "cpu").exit_code == 0
    report = io.sidecars(destination / "side.wav")[1]
    original = report.read_bytes()

    result = invoke(sources, destination, "--dry-run", "--skip-existing", "--device", "cpu")
    assert result.exit_code == 0, result.output
    assert "already done" in result.output
    assert list(destination.iterdir()) == [report]
    assert report.read_bytes() == original


def test_batch_destination_error_is_a_sentence(sources, tmp_path):
    destination = tmp_path / "not-a-folder"
    destination.write_text("keep", encoding="utf-8")
    result = invoke(sources, destination)
    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "Traceback" not in result.output
    assert destination.read_text(encoding="utf-8") == "keep"


@pytest.mark.parametrize("damage", ["report", "cleaned", "removed", "shape", "input"])
def test_resume_rebuilds_invalid_output_sets(sources, tmp_path, damage):
    destination = tmp_path / "cleaned"
    assert invoke(sources, destination, "--device", "cpu").exit_code == 0
    target = destination / "side.wav"
    removed, report = io.sidecars(target)
    if damage == "report":
        report.write_text("{}", encoding="utf-8")
    elif damage == "input":
        report.write_text(report.read_text(encoding="utf-8").replace("side.wav", "wrong.wav"),
                          encoding="utf-8")
    elif damage == "shape":
        sf.write(removed, np.zeros(500), 44100, subtype="PCM_16")
    else:
        (target if damage == "cleaned" else removed).write_bytes(b"not audio")

    result = invoke(sources, destination, "--skip-existing", "--device", "cpu")
    assert result.exit_code == 0, result.output
    assert "already done" not in result.output
    assert sf.info(target).frames == sf.info(removed).frames == 1000


@pytest.mark.parametrize("options", [[], ["--dry-run"]])
def test_completed_batch_does_not_load_detector(sources, tmp_path, monkeypatch, options):
    destination = tmp_path / "cleaned"
    assert invoke(sources, destination, "--device", "cpu", *options).exit_code == 0

    def unexpected(*args, **kwargs):
        pytest.fail("a completed batch must not load the detector")

    monkeypatch.setattr(cli, "_detector", unexpected)
    result = invoke(sources, destination, "--skip-existing", *options)
    assert result.exit_code == 0, result.output
    assert "0 of 1" in result.output
    assert "1 already done" in result.output


def test_batch_detector_memory_failure_is_a_sentence(sources, tmp_path, monkeypatch):
    def explode(*args, **kwargs):
        raise MemoryError("not enough memory")

    monkeypatch.setattr(cli, "_detector", explode)
    result = invoke(sources, tmp_path / "cleaned")
    assert result.exit_code == 1
    assert "ran out of memory" in result.output


def test_output_planning_resolves_each_path_once(tmp_path, monkeypatch):
    calls = 0
    real = Path.resolve

    def counted(self, *args, **kwargs):
        nonlocal calls
        calls += 1
        return real(self, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", counted)
    inputs = [tmp_path / f"source-{index}.wav" for index in range(100)]
    outputs = [tmp_path / f"output-{index}.wav" for index in range(300)]
    io.check_outputs(inputs, outputs)
    assert calls <= len(inputs) + len(outputs)


@pytest.mark.parametrize("changes", [
    {"channels": 2}, {"sample_rate": 48000}, {"duration_s": 9},
    {"clicks": [None]}, {"totals": {}}, {"input": None},
])
def test_survey_resume_rejects_invalid_report_fields(sources, tmp_path, changes):
    destination = tmp_path / "cleaned"
    assert invoke(sources, destination, "--dry-run", "--device", "cpu").exit_code == 0
    report = io.sidecars(destination / "side.wav")[1]
    built = json.loads(report.read_text(encoding="utf-8"))
    built.update(changes)
    report.write_text(json.dumps(built), encoding="utf-8")

    result = invoke(sources, destination, "--dry-run", "--skip-existing", "--device", "cpu")
    assert result.exit_code == 0, result.output
    assert "already done" not in result.output
    assert "1 of 1 surveyed" in result.output


def test_resume_checks_audio_bit_depth(sources, tmp_path):
    destination = tmp_path / "cleaned"
    assert invoke(sources, destination, "--device", "cpu").exit_code == 0
    target = destination / "side.wav"
    sf.write(target, np.zeros(1000), 44100, subtype="PCM_24")

    result = invoke(sources, destination, "--skip-existing", "--device", "cpu")
    assert result.exit_code == 0, result.output
    assert "already done" not in result.output
    assert sf.info(target).subtype == "PCM_16"


def test_batch_summary_separates_processed_skipped_and_failed(sources, tmp_path):
    destination = tmp_path / "cleaned"
    assert invoke(sources, destination, "--device", "cpu").exit_code == 0
    sf.write(sources / "new.wav", np.zeros(1000), 44100, subtype="PCM_16")
    (sources / "bad.wav").write_bytes(b"not audio")

    result = invoke(sources, destination, "--skip-existing", "--device", "cpu")
    assert result.exit_code == 1
    assert "1 of 3 cleaned" in result.output
    assert "1 already done; 1 failed" in result.output
