"""Report failures must not leave apparently complete audio sets or truncate surveys."""

from pathlib import Path

import pytest

from grooveclean import cli, io, report, review


@pytest.mark.parametrize("operation", ["clean", "revert"])
def test_report_failure_removes_the_entire_output_set(
    transfers, detector, tmp_path, monkeypatch, operation
):
    source = transfers["mono_44k_16"].path
    if operation == "revert":
        cleaned = tmp_path / "source.wav"
        cli.clean_file(source, cleaned, detector=detector)
        pair = review.open_pair(cleaned)
    target = tmp_path / "output.wav"
    report_path = io.sidecars(target)[1]
    report_path.write_text("stale report", encoding="utf-8")

    def explode(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(report, "write", explode)
    with pytest.raises(OSError, match="disk full"):
        if operation == "clean":
            cli.clean_file(source, target, detector=detector)
        else:
            review.revert(pair, [0], target)
    assert not any(path.exists() for path in (target, *io.sidecars(target)))


@pytest.mark.parametrize("failure", ["serialize", "replace"])
def test_failed_report_update_preserves_existing_report(tmp_path, monkeypatch, failure):
    target = tmp_path / "output.report.json"
    report.write({"old": True}, target)
    original = target.read_bytes()

    def explode(*args, **kwargs):
        raise OSError("cannot replace")

    built = {"new": object()} if failure == "serialize" else {"new": True}
    if failure == "replace":
        monkeypatch.setattr(Path, "replace", explode)
    with pytest.raises((TypeError, OSError)):
        report.write(built, target)
    assert target.read_bytes() == original
    assert list(tmp_path.iterdir()) == [target]
