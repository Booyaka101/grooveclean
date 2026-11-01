"""Report-only timelines: sample boundaries, overlap unions and editable input validation."""

import copy
import csv
import io
import json
import random
import subprocess
import sys

import pytest
from click.testing import CliRunner

from grooveclean import cli, report, timeline


def event(start, end, channel=0, repair="lsar"):
    return report.Click(channel, start, end, end - start, 0.8, 0.1, repair)


def built(clicks=(), frames=2500, rate=1000, channels=2):
    return report.build(input_path="missing.wav", sample_rate=rate, channels=channels,
                        frames=frames, clicks=clicks)


def test_crossing_overlaps_channels_and_unrepaired():
    source = built([event(900, 1200), event(1000, 1300), event(1100, 1150),
                    event(1000, 1500, 1), event(2000, 2500, 1, "unrepaired")])
    original = copy.deepcopy(source)
    result = timeline.build(source, 1)
    first, second, last = result["buckets"]
    assert [r["events"] for r in result["buckets"]] == [1, 3, 1]
    assert first["repaired_pct"] == 5
    assert second["repaired_pct"] == 40
    assert second["channels"][0]["repaired_samples"] == 300
    assert second["channels"][1]["repaired_samples"] == 500
    assert last["events_per_second"] == 2
    assert last["unrepaired_events"] == 1
    assert last["repaired_pct"] == 0
    assert source == original


def test_full_stereo_coverage_is_not_over_100_percent():
    rows = timeline.build(built([event(0, 2500), event(0, 2500, 1)]), 1)["buckets"]
    assert [r["repaired_pct"] for r in rows] == [100, 100, 100]


def test_empty_zero_and_exact_boundaries():
    assert timeline.build(built(frames=0))["buckets"] == []
    rows = timeline.build(built(frames=2000), 1)["buckets"]
    assert len(rows) == 2
    assert all(r["events"] == r["repaired_pct"] == 0 for r in rows)
    rows = timeline.build(built([event(999, 1000), event(1000, 1001)], frames=2000), 1)["buckets"]
    assert [r["events"] for r in rows] == [1, 1]
    assert [r["repaired_channel_samples"] for r in rows] == [1, 1]


def test_duration_rounding_preserves_valid_endpoint():
    source = built([event(44090, 44110)], frames=44110, rate=44100, channels=1)
    result = timeline.build(source, 1)
    assert result["reported_duration_s"] == 1
    assert result["buckets"][-1]["end_sample"] == 44110
    assert sum(r["repaired_channel_samples"] for r in result["buckets"]) == 20
    source["clicks"][0].update(end_sample=44123, width_samples=33)
    with pytest.raises(ValueError, match="outside"):
        timeline.build(source)
    assert timeline.build(built([event(0, 1)], frames=1, rate=44100))["duration_s"] > 0


@pytest.mark.parametrize("key,value", [
    ("sample_rate", True), ("sample_rate", 0), ("channels", -1), ("channels", 1.5),
    ("duration_s", float("nan")), ("duration_s", float("inf")), ("duration_s", -1),
    ("clicks", {}),
])
def test_invalid_metadata(key, value):
    source = built()
    source[key] = value
    with pytest.raises(ValueError):
        timeline.build(source)


@pytest.mark.parametrize("key,value", [
    ("channel", True), ("channel", 2), ("start_sample", -1), ("end_sample", 2600),
    ("width_samples", 3), ("confidence", float("nan")), ("residual_rms", -1),
    ("repair", "unknown"),
])
def test_invalid_clicks(key, value):
    source = built([event(0, 2)])
    source["clicks"][0][key] = value
    with pytest.raises(ValueError, match="click 1"):
        timeline.build(source)


@pytest.mark.parametrize("seconds", [0, -1, float("nan"), float("inf"), 0.00001])
def test_invalid_bucket_size(seconds):
    with pytest.raises(ValueError, match="bucket"):
        timeline.build(built(), seconds)


def test_resource_limit():
    with pytest.raises(ValueError, match="too many"):
        timeline.build(built(frames=1000000), 0.001)


def test_union_matches_sample_mask_for_shuffled_spans():
    rng = random.Random(7)
    clicks = []
    masks = [[False] * 2500 for _ in range(2)]
    for _ in range(100):
        start = rng.randrange(2500)
        end = rng.randrange(start + 1, 2501)
        channel = rng.randrange(2)
        method = rng.choice(["lsar", "cubic", "unrepaired"])
        clicks.append(event(start, end, channel, method))
        if method != "unrepaired":
            masks[channel][start:end] = [True] * (end - start)
    rng.shuffle(clicks)
    rows = timeline.build(built(clicks), 0.3)["buckets"]
    for row in rows:
        start, end = row["start_sample"], row["end_sample"]
        for ch in row["channels"]:
            assert ch["repaired_samples"] == sum(masks[ch["channel"]][start:end])
            assert ch["events"] == sum(
                start <= e.start_sample < end and e.channel == ch["channel"] for e in clicks
            )


def test_timeline_module_does_not_import_audio_or_models():
    result = subprocess.run(
        [sys.executable, "-c", "import sys; from grooveclean import timeline; "
         "assert not {'torch', 'numpy', 'soundfile'} & sys.modules.keys()"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr


def test_cli_formats_sorting_and_no_audio_access(tmp_path, monkeypatch):
    source = tmp_path / "side.report.json"
    source.write_text(json.dumps(built([event(1900, 2200)])), encoding="utf-8")
    before = source.read_bytes()

    def forbidden(*args, **kwargs):
        pytest.fail("timeline must not access audio or detector weights")

    monkeypatch.setattr(cli.io, "probe", forbidden)
    monkeypatch.setattr(cli.detect, "Detector", forbidden)
    runner = CliRunner()
    common = ["timeline", str(source), "--bucket-seconds", "1"]
    result = runner.invoke(
        cli.main, [*common, "--format", "json", "--sort", "coverage", "--top", "1"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["buckets"][0]["start_s"] == 2
    result = runner.invoke(cli.main, [*common, "--format", "csv"])
    assert result.exit_code == 0, result.output
    rows = list(csv.DictReader(io.StringIO(result.output)))
    assert len(rows) == 6
    assert rows[-2]["repaired_samples"] == "200"
    result = runner.invoke(cli.main, [*common, "--sort", "events", "--top", "1"])
    assert result.exit_code == 0, result.output
    assert "1.000-2.000" in result.output
    assert "channel-normalized" in result.output
    assert source.read_bytes() == before
    assert list(tmp_path.iterdir()) == [source]


@pytest.mark.parametrize("content", ["[]", "null", "{", '{"clicks": []}'])
def test_bad_report_is_cli_error(tmp_path, content):
    path = tmp_path / "bad.json"
    path.write_text(content, encoding="utf-8")
    result = CliRunner().invoke(cli.main, ["timeline", str(path)])
    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "Traceback" not in result.output
