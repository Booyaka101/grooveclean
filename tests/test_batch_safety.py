"""Batch planning must not overwrite another source or another result."""

import os

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
