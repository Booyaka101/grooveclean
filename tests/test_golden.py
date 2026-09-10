"""Group 4: the bundled 78 excerpt has to keep producing the click count that is checked in.

This is a regression guard, not a measure of quality. Any change to detection, thresholds or
repair that moves the count on a real 1917 transfer by more than 2% has to be deliberate, and
refreshing the number is a visible edit to tests/data/ASSETS.json.
"""

from __future__ import annotations

import pytest

from conftest import DATA
from grooveclean import cli, io


@pytest.fixture(scope="module")
def golden(assets) -> dict:
    if "golden" not in assets:
        pytest.skip("no golden count recorded; run python train/fetch_test_assets.py --golden")
    return assets["golden"]


@pytest.fixture(scope="module")
def cleaned(detector, tmp_path_factory) -> dict:
    out = tmp_path_factory.mktemp("golden") / "excerpt78.wav"
    return cli.clean_file(DATA / "excerpt78.flac", out, detector=detector)


def test_the_excerpt_is_the_one_we_pinned(assets):
    entry = next(a for a in assets["assets"] if a["file"] == "excerpt78.flac")
    info = io.probe(DATA / "excerpt78.flac")
    assert info.samplerate == entry["sample_rate"]
    assert info.channels == entry["channels"]
    assert info.duration_s == pytest.approx(entry["seconds"], abs=0.01)


def test_click_count_matches_the_checked_in_expectation(cleaned, golden):
    expected, found = golden["clicks"], cleaned["totals"]["count"]
    tolerance = golden["tolerance"]
    assert abs(found - expected) <= max(1, round(tolerance * expected)), (
        f"{found} clicks against a pinned {expected} "
        f"(more than {tolerance * 100:.0f}% out; refresh ASSETS.json if this was intended)"
    )


def test_the_78_excerpt_actually_has_crackle_on_it(cleaned):
    """A golden count of nearly zero would pass the test above and mean nothing."""
    assert cleaned["totals"]["count"] > 50
    assert cleaned["totals"]["pct_of_duration"] > 0.0
