"""Report-only damage summaries. No audio, detector or model dependencies."""

from __future__ import annotations

import math
import sys

from .report import check_click, is_finite_number

MAX_BUCKETS = 100_000
SORT_KEYS = {
    "time": lambda row: row["start_sample"],
    "coverage": lambda row: (-row["repaired_pct"], row["start_sample"]),
    "events": lambda row: (-row["events_per_second"], row["start_sample"]),
    "unrepaired": lambda row: (-row["unrepaired_events_per_second"], row["start_sample"]),
}


def build(built: dict, bucket_seconds: float = 10.0) -> dict:
    """Count onsets and union repaired coverage per channel in sample-aligned buckets.

    Reports round duration to milliseconds. Use its nominal frame count, extended
    to the last event endpoint only within that rounding uncertainty.
    """
    if not isinstance(built, dict):
        raise ValueError("expected a report object")
    rate, channels = built.get("sample_rate"), built.get("channels")
    duration, clicks = built.get("duration_s"), built.get("clicks")
    if type(rate) is not int or not 0 < rate <= sys.maxsize:
        raise ValueError("sample_rate must be a positive integer within system limits")
    if type(channels) is not int or not 0 < channels <= MAX_BUCKETS:
        raise ValueError(f"channels must be a positive integer no greater than {MAX_BUCKETS}")
    if (not is_finite_number(duration) or duration < 0
            or not is_finite_number(duration * rate) or duration * rate > sys.maxsize):
        raise ValueError("duration_s must be finite and nonnegative")
    if not isinstance(clicks, list):
        raise ValueError("clicks must be a list")
    if (not is_finite_number(bucket_seconds) or bucket_seconds <= 0
            or not is_finite_number(bucket_seconds * rate)):
        raise ValueError("bucket seconds must be finite and positive")
    width = round(bucket_seconds * rate)
    if width < 1:
        raise ValueError("bucket seconds must span at least one sample")
    nominal = round(duration * rate)
    # Small epsilon accommodates binary representation of the millisecond boundary.
    limit = math.floor((duration + 0.0005) * rate + 1e-7)
    frames = nominal
    for position, entry in enumerate(clicks, 1):
        check_click(entry, position, channels=channels, frames=limit)
        frames = max(frames, entry["end_sample"])
    count = (frames + width - 1) // width
    if count > MAX_BUCKETS or count * channels > MAX_BUCKETS:
        raise ValueError("too many timeline buckets/channels; increase --bucket-seconds")
    rows = []
    for start in range(0, frames, width):
        end = min(start + width, frames)
        rows.append({
            "start_sample": start, "end_sample": end,
            "start_s": start / rate, "end_s": end / rate,
            "events": 0, "unrepaired_events": 0,
            "channels": [{"channel": ch, "events": 0, "unrepaired_events": 0,
                          "repaired_samples": 0} for ch in range(channels)],
        })
    spans = [[] for _ in range(channels)] if clicks else []
    for entry in clicks:
        ch, start, end = entry["channel"], entry["start_sample"], entry["end_sample"]
        row = rows[start // width]
        row["events"] += 1
        row["channels"][ch]["events"] += 1
        if entry["repair"] == "unrepaired":
            row["unrepaired_events"] += 1
            row["channels"][ch]["unrepaired_events"] += 1
        else:
            spans[ch].append((start, end))
    for ch, intervals in enumerate(spans):
        covered_until = 0
        for start, end in sorted(intervals):
            start = max(start, covered_until)
            if start >= end:
                continue
            covered_until = end
            for index in range(start // width, (end - 1) // width + 1):
                row = rows[index]
                row["channels"][ch]["repaired_samples"] += (
                    min(end, row["end_sample"]) - max(start, row["start_sample"])
                )
    for row in rows:
        length = row["end_sample"] - row["start_sample"]
        row["events_per_second"] = row["events"] * rate / length
        row["unrepaired_events_per_second"] = row["unrepaired_events"] * rate / length
        repaired = 0
        for channel in row["channels"]:
            repaired += channel["repaired_samples"]
            channel["repaired_pct"] = 100 * channel["repaired_samples"] / length
            channel["events_per_second"] = channel["events"] * rate / length
            channel["unrepaired_events_per_second"] = channel["unrepaired_events"] * rate / length
        row["repaired_channel_samples"] = repaired
        row["repaired_pct"] = 100 * repaired / (length * channels)
    summary = {"events": len(clicks), "unrepaired_events": 0, "repaired_channel_samples": 0,
               "channels": []}
    for ch in range(channels):
        totals = {"channel": ch, "events": 0, "unrepaired_events": 0, "repaired_samples": 0}
        for row in rows:
            for key in ("events", "unrepaired_events", "repaired_samples"):
                totals[key] += row["channels"][ch][key]
        totals["repaired_pct"] = 100 * totals["repaired_samples"] / frames if frames else 0.0
        totals["events_per_second"] = totals["events"] * rate / frames if frames else 0.0
        summary["channels"].append(totals)
        summary["unrepaired_events"] += totals["unrepaired_events"]
        summary["repaired_channel_samples"] += totals["repaired_samples"]
    summary["repaired_pct"] = (
        100 * summary["repaired_channel_samples"] / (frames * channels) if frames else 0.0
    )
    summary["events_per_second"] = len(clicks) * rate / frames if frames else 0.0
    return {
        "schema_version": 1, "summary": summary, "total_buckets": len(rows),
        "sample_rate": rate, "channels": channels,
        "reported_duration_s": duration, "duration_s": frames / rate,
        "duration_precision_s": 0.001,
        "bucket_seconds": width / rate, "buckets": rows,
    }
