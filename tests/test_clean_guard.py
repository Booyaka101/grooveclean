"""Group 2: on audio with no clicks in it, the difference file has to be silent."""

from __future__ import annotations

import json

import numpy as np

from conftest import DATA, read_exact
from grooveclean import cli

SILENT_DBFS = -80.0


def peak_dbfs(data: np.ndarray) -> float:
    peak = float(np.abs(data).max()) if data.size else 0.0
    return 20.0 * float(np.log10(peak)) if peak > 0.0 else -np.inf


def test_clean_music_produces_a_silent_difference(clean_transfer, detector, tmp_path):
    out = tmp_path / "clean.out.wav"
    built = cli.clean_file(clean_transfer, out, detector=detector)
    removed_path, report_path = cli.sidecars(out)

    assert out.exists() and removed_path.exists() and report_path.exists()
    assert peak_dbfs(read_exact(removed_path)) < SILENT_DBFS
    assert built["totals"] == {"count": 0, "samples_repaired": 0, "pct_of_duration": 0.0}
    assert json.loads(report_path.read_text(encoding="utf-8")) == built


def test_a_real_clean_release_is_left_alone(assets, detector, tmp_path):
    source = DATA / "clean_excerpt.flac"
    out = tmp_path / "release.out.wav"
    cli.clean_file(source, out, detector=detector)
    assert peak_dbfs(read_exact(cli.sidecars(out)[0])) < SILENT_DBFS


def test_zero_clicks_still_writes_all_three_files(clean_transfer, detector, tmp_path):
    out = tmp_path / "nested" / "deeper" / "out.wav"
    cli.clean_file(clean_transfer, out, detector=detector)
    removed_path, report_path = cli.sidecars(out)

    assert removed_path.name == "out.removed.wav"
    assert report_path.name == "out.report.json"
    original, cleaned = read_exact(clean_transfer), read_exact(out)
    assert np.array_equal(cleaned, original)
    assert read_exact(removed_path).shape == original.shape
