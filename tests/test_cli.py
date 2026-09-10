"""Group 5: the command line itself. Every failure has to read as a sentence, not a traceback."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf
import torch
from click.testing import CliRunner

from conftest import LAYOUTS, music, write
from grooveclean import __version__, cli
from grooveclean.cli import main, sidecars


@pytest.fixture()
def run():
    runner = CliRunner()
    return lambda *args: runner.invoke(main, [str(a) for a in args], catch_exceptions=False)


@pytest.mark.parametrize("name", sorted(LAYOUTS))
def test_clean_exits_zero_on_every_layout(run, transfers, tmp_path, name):
    transfer = transfers[name]
    out = tmp_path / f"{name}.wav"
    result = run("clean", transfer.path, "-o", out)

    assert result.exit_code == 0, result.output
    assert out.exists()
    report = json.loads(sidecars(out)[1].read_text(encoding="utf-8"))
    assert report["sample_rate"] == transfer.rate
    assert f"{transfer.rate} Hz" in result.output
    assert f"{transfer.channels}ch" in result.output
    assert "detected" in result.output and "repaired in" in result.output


def test_lossy_input_is_refused_with_an_explanation(run, tmp_path):
    rate = 44100
    source = tmp_path / "rip.mp3"
    write(source, music(rate, 2.0, 2, np.random.default_rng(3)), rate, "MPEG_LAYER_III")

    result = run("clean", source, "-o", tmp_path / "out.wav")
    assert result.exit_code != 0
    assert "Traceback" not in result.output
    assert "lossy" in result.output.lower()
    assert "mp3" in result.output.lower()
    assert "uncompressed PCM and FLAC" in result.output


def test_a_missing_file_says_so(run, tmp_path):
    result = run("clean", tmp_path / "nope.wav", "-o", tmp_path / "out.wav")
    assert result.exit_code != 0
    assert "no such file" in result.output.lower()
    assert "Traceback" not in result.output


def test_a_directory_is_not_an_audio_file(run, tmp_path):
    result = run("clean", tmp_path, "-o", tmp_path / "out.wav")
    assert result.exit_code != 0
    assert "is a directory" in result.output


def test_a_file_that_is_not_audio_at_all(run, tmp_path):
    source = tmp_path / "sleeve.jpg"
    source.write_bytes(b"\xff\xd8\xff\xe0not really a jpeg either")
    result = run("clean", source, "-o", tmp_path / "out.wav")
    assert result.exit_code != 0
    assert "cannot read as audio" in result.output
    assert "Traceback" not in result.output


def test_an_empty_file_is_rejected(run, tmp_path):
    source = tmp_path / "empty.wav"
    sf.write(str(source), np.zeros((0, 1)), 44100, subtype="PCM_16")
    result = run("clean", source, "-o", tmp_path / "out.wav")
    assert result.exit_code != 0
    assert "no audio frames" in result.output


def test_sensitivity_is_bounded(run, transfers, tmp_path):
    result = run(
        "clean", transfers["mono_44k_16"].path, "-o", tmp_path / "o.wav", "--sensitivity", "9"
    )
    assert result.exit_code != 0
    assert "9" in result.output and "1" in result.output


def folder_of(transfers, tmp_path, *names: str) -> Path:
    """A source directory holding copies of the named fixture transfers, one WAV each."""
    source_dir = tmp_path / "side"
    source_dir.mkdir(exist_ok=True)
    for name in names:
        data, rate = sf.read(str(transfers[name].path), always_2d=True)
        sf.write(str(source_dir / f"{name}.wav"), data, rate, subtype=transfers[name].subtype)
    return source_dir


def test_batch_cleans_a_whole_folder(run, transfers, tmp_path):
    source_dir = folder_of(transfers, tmp_path, "mono_44k_16", "stereo_44k_24")
    result = run("batch", source_dir, "-o", tmp_path / "done")
    assert result.exit_code == 0, result.output
    produced = sorted(p.name for p in (tmp_path / "done").iterdir())
    assert produced == [
        "mono_44k_16.removed.wav",
        "mono_44k_16.report.json",
        "mono_44k_16.wav",
        "stereo_44k_24.removed.wav",
        "stereo_44k_24.report.json",
        "stereo_44k_24.wav",
    ]
    assert "2 of 2 cleaned" in result.output


def test_batch_defaults_to_a_cleaned_subfolder(run, transfers, tmp_path):
    source_dir = folder_of(transfers, tmp_path, "mono_44k_16")
    assert run("batch", source_dir).exit_code == 0
    assert (source_dir / "cleaned" / "mono_44k_16.wav").exists()


def test_batch_refuses_to_overwrite_its_own_input(run, transfers, tmp_path):
    source_dir = folder_of(transfers, tmp_path, "mono_44k_16")
    result = run("batch", source_dir, "-o", source_dir)
    assert result.exit_code != 0
    assert "would overwrite the input files" in result.output


def test_batch_keeps_going_past_a_bad_file(run, transfers, tmp_path):
    source_dir = folder_of(transfers, tmp_path, "mono_44k_16")
    (source_dir / "bad.wav").write_bytes(b"RIFF" + bytes(4) + b"WAVEjunk")

    result = run("batch", source_dir, "-o", tmp_path / "done")
    assert result.exit_code != 0
    assert "bad.wav: skipped" in result.output
    assert "1 of 2 cleaned" in result.output
    assert (tmp_path / "done" / "mono_44k_16.wav").exists()


def test_batch_on_an_empty_folder(run, tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    result = run("batch", empty)
    assert result.exit_code != 0
    assert "no audio files to clean" in result.output


def test_batch_on_a_missing_folder(run, tmp_path):
    result = run("batch", tmp_path / "gone")
    assert result.exit_code != 0
    assert "no such directory" in result.output


def test_version_and_help(run):
    version = run("--version")
    assert version.exit_code == 0 and __version__ in version.output
    for args in (("--help",), ("clean", "--help"), ("batch", "--help")):
        result = run(*args)
        assert result.exit_code == 0
        assert "sensitivity" in result.output or "Declick" in result.output


def test_cuda_falls_back_to_cpu_without_a_gpu(run, transfers, tmp_path, monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    result = run(
        "clean", transfers["mono_44k_16"].path, "-o", tmp_path / "o.wav", "--device", "cuda"
    )
    assert result.exit_code == 0, result.output
    assert "cuda was requested but is not available" in result.output
    assert "on cpu" in result.output


def test_a_missing_weights_override_is_reported(run, transfers, tmp_path):
    result = run(
        "clean", transfers["mono_44k_16"].path, "-o", tmp_path / "o.wav",
        "--weights", tmp_path / "nothing.pt",
    )
    assert result.exit_code != 0
    assert "weights not found" in result.output
    assert "Traceback" not in result.output


@pytest.mark.parametrize("stem", ["same", "same.removed"])
def test_writing_over_the_input_is_refused(run, transfers, tmp_path, stem):
    """-o pointing at the source, or at a name whose difference file would be the source."""
    source = tmp_path / f"{stem}.wav"
    data, rate = sf.read(str(transfers["mono_44k_16"].path), always_2d=True)
    sf.write(str(source), data, rate, subtype="PCM_16")
    before = source.read_bytes()

    result = run("clean", source, "-o", tmp_path / "same.wav")
    assert result.exit_code != 0
    assert "is the input file" in result.output
    assert source.read_bytes() == before


def test_a_weights_file_that_is_not_a_checkpoint(run, transfers, tmp_path):
    junk = tmp_path / "notes.pt"
    torch.save({"hello": 1}, str(junk))
    result = run(
        "clean", transfers["mono_44k_16"].path, "-o", tmp_path / "o.wav", "--weights", junk
    )
    assert result.exit_code != 0
    assert "not a grooveclean detector checkpoint" in result.output
    assert "Traceback" not in result.output


def test_a_failure_part_way_through_leaves_no_half_written_files(
    transfers, detector, tmp_path, monkeypatch
):
    """A truncated side and its difference file look exactly like a finished pair."""
    calls = []

    def explode(*args, **kwargs):
        calls.append(1)
        if len(calls) > 1:
            raise MemoryError("out of memory")
        return real(*args, **kwargs)

    real = cli._process_block
    monkeypatch.setattr(cli, "CORE_SECONDS", 0.5)
    monkeypatch.setattr(cli, "_process_block", explode)
    out = tmp_path / "half.wav"
    with pytest.raises(MemoryError):
        cli.clean_file(transfers["stereo_44k_24"].path, out, detector=detector)
    assert not out.exists()
    assert not cli.sidecars(out)[0].exists()


def test_dry_run_writes_the_report_and_no_audio(run, transfers, tmp_path):
    out = tmp_path / "survey.wav"
    result = run("clean", transfers["stereo_44k_24"].path, "-o", out, "--dry-run")
    assert result.exit_code == 0, result.output
    removed_path, report_path = sidecars(out)
    assert not out.exists() and not removed_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["totals"]["count"] > 0
    assert "surveyed in" in result.output and "repaired in" not in result.output


def test_dry_run_agrees_with_the_real_thing(transfers, detector, tmp_path):
    transfer = transfers["stereo_44k_24"]
    wet = cli.clean_file(transfer.path, tmp_path / "wet.wav", detector=detector)
    dry = cli.clean_file(transfer.path, tmp_path / "dry.wav", detector=detector, report_only=True)
    assert dry["clicks"] == wet["clicks"]


def test_batch_dry_run_says_surveyed(run, transfers, tmp_path):
    source_dir = folder_of(transfers, tmp_path, "mono_44k_16")
    result = run("batch", source_dir, "-o", tmp_path / "done", "--dry-run")
    assert result.exit_code == 0, result.output
    assert "1 of 1 surveyed" in result.output
    assert sorted(p.name for p in (tmp_path / "done").iterdir()) == ["mono_44k_16.report.json"]


def test_a_cuda_out_of_memory_reads_as_a_sentence(run, transfers, tmp_path, monkeypatch):
    """torch raises a RuntimeError subclass for this, so catching MemoryError is not enough."""

    def explode(*args, **kwargs):
        raise torch.cuda.OutOfMemoryError("CUDA out of memory. Tried to allocate 2.00 GiB")

    monkeypatch.setattr(cli, "_process_block", explode)
    result = run("clean", transfers["mono_44k_16"].path, "-o", tmp_path / "o.wav")
    assert result.exit_code != 0
    assert "ran out of memory" in result.output
    assert "Traceback" not in result.output


def test_a_container_that_cannot_hold_the_input_is_refused(run, tmp_path):
    """FLAC has no float subtype, and finding that out after an hour of work is no use."""
    rate = 44100
    source = tmp_path / "float.wav"
    write(source, music(rate, 1.0, 1, np.random.default_rng(5)), rate, "FLOAT")

    for extra in ([], ["--dry-run"]):
        result = run("clean", source, "-o", tmp_path / "o.flac", *extra)
        assert result.exit_code != 0
        assert "FLAC cannot hold FLOAT audio" in result.output


def test_an_output_name_with_no_known_format_is_refused(run, transfers, tmp_path):
    """Guessing WAV for -o side.xyz writes a file nothing will open by its name."""
    source = transfers["mono_44k_16"].path
    for name in ("o.xyz", "o"):
        result = run("clean", source, "-o", tmp_path / name)
        assert result.exit_code != 0
        assert "cannot tell the format from that name" in result.output
        assert not (tmp_path / name).exists()

    assert run("clean", source, "-o", tmp_path / "o.wave").exit_code == 0
    assert sf.info(str(tmp_path / "o.wave")).format == "WAV"


def test_a_truncated_file_says_where_it_stops(run, transfers, tmp_path):
    """FLAC keeps the length in its header, so a half-copied file reads short with no error."""
    data, rate = sf.read(str(transfers["stereo_44k_24"].path), always_2d=True)
    whole = tmp_path / "whole.flac"
    sf.write(str(whole), data, rate, subtype="PCM_24")
    source = tmp_path / "cut.flac"
    source.write_bytes(whole.read_bytes()[: whole.stat().st_size // 2])

    result = run("clean", source, "-o", tmp_path / "o.wav")
    assert result.exit_code != 0
    assert "read failed at frame" in result.output
    assert "Traceback" not in result.output


def test_an_output_path_that_cannot_be_opened(run, transfers, tmp_path):
    taken = tmp_path / "busy.wav"
    taken.mkdir()
    result = run("clean", transfers["mono_44k_16"].path, "-o", taken)
    assert result.exit_code != 0
    assert "cannot be written" in result.output
    assert "Traceback" not in result.output


def test_skip_existing_resumes_a_batch(run, transfers, tmp_path):
    source_dir = folder_of(transfers, tmp_path, "mono_44k_16", "stereo_44k_24")
    done = tmp_path / "done"
    assert run("batch", source_dir, "-o", done).exit_code == 0
    first = (done / "mono_44k_16.wav").stat().st_mtime_ns

    result = run("batch", source_dir, "-o", done, "--skip-existing")
    assert result.exit_code == 0, result.output
    assert result.output.count("already done") == 2
    assert (done / "mono_44k_16.wav").stat().st_mtime_ns == first


def test_batch_can_write_flac(run, transfers, tmp_path):
    """A stack of 96 kHz sides is a lot of disk, and the report has to follow the audio."""
    source_dir = folder_of(transfers, tmp_path, "mono_44k_16", "stereo_44k_24")
    done = tmp_path / "done"
    result = run("batch", source_dir, "-o", done, "--format", "flac")

    assert result.exit_code == 0, result.output
    assert sorted(p.name for p in done.iterdir()) == [
        "mono_44k_16.flac",
        "mono_44k_16.removed.flac",
        "mono_44k_16.report.json",
        "stereo_44k_24.flac",
        "stereo_44k_24.removed.flac",
        "stereo_44k_24.report.json",
    ]
    assert sf.info(str(done / "stereo_44k_24.flac")).subtype == "PCM_24"
