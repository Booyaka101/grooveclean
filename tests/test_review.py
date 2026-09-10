"""Group 6: auditing a run and putting repairs back. Both live off the difference file."""

from __future__ import annotations

import json

import numpy as np
import pytest
from click.testing import CliRunner

from conftest import LAYOUTS, read_exact
from grooveclean import cli, io, review
from grooveclean.cli import main

TOLERANCE = 1e-6  # float files round through float32; integer files have to be exact


@pytest.fixture()
def run():
    runner = CliRunner()
    return lambda *args: runner.invoke(main, [str(a) for a in args], catch_exceptions=False)


@pytest.fixture()
def cleaned(transfers, detector, tmp_path):
    """A cleaned stereo file with its difference file and report, ready to review."""
    out = tmp_path / "side.wav"
    built = cli.clean_file(transfers["stereo_44k_24"].path, out, detector=detector)
    assert built["totals"]["count"] > 8, "the fixture needs enough clicks to select from"
    return out


@pytest.mark.parametrize("name", sorted(LAYOUTS))
def test_reverting_every_repair_gives_the_input_back(transfers, detector, tmp_path, name):
    source = transfers[name].path
    out = tmp_path / f"{name}.wav"
    built = cli.clean_file(source, out, detector=detector)
    pair = review.open_pair(out)
    chosen = review.select(pair.clicks, rate=pair.cleaned.samplerate)

    again = review.revert(pair, chosen, tmp_path / f"{name}.back.wav")

    original, restored = read_exact(source), read_exact(tmp_path / f"{name}.back.wav")
    assert np.abs(restored - original).max() <= TOLERANCE
    assert np.abs(read_exact(io.sidecars(tmp_path / f"{name}.back.wav")[0])).max() <= TOLERANCE
    assert again["totals"] == {"count": 0, "samples_repaired": 0, "pct_of_duration": 0.0}
    assert built["totals"]["count"] >= len(chosen)


def test_revert_moves_only_the_named_repairs(cleaned, tmp_path):
    pair = review.open_pair(cleaned)
    chosen = [1, 4, 5]
    picked = [pair.clicks[i] for i in chosen]

    review.revert(pair, chosen, tmp_path / "fixed.wav")

    before, after = read_exact(cleaned), read_exact(tmp_path / "fixed.wav")
    moved = np.zeros(before.shape, dtype=bool)
    for entry in picked:
        moved[entry["start_sample"] : entry["end_sample"], entry["channel"]] = True
    assert not (before != after)[~moved].any(), "a span nobody asked for changed"
    assert (before != after).any(), "the named repairs did not come back"
    kept = json.loads(io.sidecars(tmp_path / "fixed.wav")[1].read_text(encoding="utf-8"))
    assert kept["totals"]["count"] == pair.report["totals"]["count"] - len(chosen)


def test_reverted_pair_still_adds_back_up(transfers, cleaned, tmp_path):
    pair = review.open_pair(cleaned)
    review.revert(pair, [0, 2], tmp_path / "fixed.wav")

    original = read_exact(transfers["stereo_44k_24"].path)
    fixed, removed = (
        read_exact(p) for p in (tmp_path / "fixed.wav", io.sidecars(tmp_path / "fixed.wav")[0])
    )
    assert np.abs(fixed + removed - original).max() <= TOLERANCE


def test_audit_excerpts_are_aligned_and_come_from_the_two_files(transfers, cleaned, tmp_path):
    pair = review.open_pair(cleaned)
    chosen = review.rank(pair.clicks, review.select(pair.clicks, rate=44100), "removed", 5)
    before_path, after_path = tmp_path / "a.before.wav", tmp_path / "a.after.wav"

    rows = review.audit(pair, chosen, before_path, after_path, context_ms=100.0)

    before, after = read_exact(before_path), read_exact(after_path)
    assert before.shape == after.shape
    assert (before != after).any()
    assert {index for _, index in rows} == set(chosen)

    original, repaired = read_exact(transfers["stereo_44k_24"].path), read_exact(cleaned)
    cut = review.windows(pair.clicks, chosen, int(0.1 * 44100), pair.cleaned.frames)
    gap = int(round(review.GAP_MS * 1e-3 * 44100))
    at = 0
    for number, (low, high, _) in enumerate(cut):
        at += gap if number else 0
        assert np.abs(before[at : at + high - low] - original[low:high]).max() <= TOLERANCE
        assert np.abs(after[at : at + high - low] - repaired[low:high]).max() <= TOLERANCE
        at += high - low
    assert at == before.shape[0], "the excerpts and gaps do not account for the whole file"


def test_windows_merge_when_two_clicks_share_their_context():
    clicks = [
        {"start_sample": 1000, "end_sample": 1010},
        {"start_sample": 1200, "end_sample": 1210},
        {"start_sample": 9000, "end_sample": 9010},
    ]
    merged = review.windows(clicks, [0, 1, 2], context=300, frames=20000)

    assert [(low, high, members) for low, high, members in merged] == [
        (700, 1510, [0, 1]),
        (8700, 9310, [2]),
    ]


@pytest.mark.parametrize(
    ("text", "expected"),
    [("3", {3}), ("3,17,204", {3, 17, 204}), ("12-15", {12, 13, 14, 15}), ("1, 3-4", {1, 3, 4})],
)
def test_parse_indices_reads_numbers_and_ranges(text, expected):
    assert review.parse_indices(text, 300) == expected


@pytest.mark.parametrize("text", ["0", "301", "9-4", "eight", "3-"])
def test_parse_indices_refuses_nonsense(text):
    with pytest.raises(review.ReviewError):
        review.parse_indices(text, 300)


@pytest.mark.parametrize(
    ("text", "seconds"), [("92", 92.0), ("1:32", 92.0), ("1:32.415", 92.415), ("0:00", 0.0)]
)
def test_parse_time_reads_a_player_position(text, seconds):
    assert review.parse_time(text) == pytest.approx(seconds)


def test_select_between_takes_the_repairs_that_overlap_that_stretch():
    clicks = [
        {"start_sample": 100, "end_sample": 110, "repair": "lsar"},
        {"start_sample": 4_400, "end_sample": 4_500, "repair": "lsar"},
        {"start_sample": 90_000, "end_sample": 90_010, "repair": "lsar"},
    ]
    assert review.select(clicks, rate=44100, between="0:00.05-0:01.5") == [1]


@pytest.mark.parametrize("text", ["1:32", "5-2", "-", "a-b"])
def test_parse_span_refuses_nonsense(text):
    with pytest.raises(review.ReviewError):
        review.parse_span(text, 44100)


def test_select_skips_spans_that_were_never_repaired():
    clicks = [
        {"width_samples": 10, "confidence": 0.9, "repair": "lsar"},
        {"width_samples": 99, "confidence": 0.9, "repair": "unrepaired"},
    ]
    assert review.select(clicks, rate=44100) == [0]
    assert review.select(clicks, rate=44100, indices="1,2") == [0]


def test_audit_then_revert_from_the_command_line(run, cleaned, tmp_path):
    audited = run("audit", cleaned, "--top", 3)
    assert audited.exit_code == 0, audited.output
    assert "excerpt  click" in audited.output
    assert "removed dBFS" in audited.output
    numbers = [int(line.split()[1]) for line in audited.output.splitlines()[1:4]]

    reverted = run("revert", cleaned, "-o", tmp_path / "fixed.wav", "--clicks", numbers[0])
    assert reverted.exit_code == 0, reverted.output
    assert "put back 1 of" in reverted.output


def test_review_without_the_sidecars_reads_as_a_sentence(run, transfers, tmp_path):
    result = run("audit", transfers["mono_44k_16"].path)

    assert result.exit_code != 0
    assert "keep them together" in result.output
    assert "Traceback" not in result.output


def test_revert_refuses_to_undo_everything_by_accident(run, cleaned, tmp_path):
    result = run("revert", cleaned, "-o", tmp_path / "fixed.wav")

    assert result.exit_code != 0
    assert "--clicks" in result.output


def test_revert_refuses_to_write_over_its_own_input(run, cleaned):
    result = run("revert", cleaned, "-o", cleaned, "--clicks", "1")

    assert result.exit_code != 0
    assert "choose another -o" in result.output
