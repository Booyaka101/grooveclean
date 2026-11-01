"""JSON report emission for a cleaning run."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


def is_finite_number(value: object) -> bool:
    """JSON numbers may be huge integers as well as NaN/Infinity extensions."""
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def check_click(entry: dict, position: int, *, channels: int, frames: int) -> None:
    """Validate editable report records before indexing audio or aggregating spans."""
    fields = ("channel", "start_sample", "end_sample", "width_samples", "confidence",
              "residual_rms", "repair")
    if not isinstance(entry, dict) or any(field not in entry for field in fields):
        raise ValueError(f"click {position} is missing fields")
    start, end, channel = entry["start_sample"], entry["end_sample"], entry["channel"]
    if not all(type(value) is int for value in (start, end, channel)):
        raise ValueError(f"click {position} has a position that is not a whole number")
    if not 0 <= channel < channels:
        raise ValueError(f"click {position} is on channel {channel} of a {channels}-channel file")
    if not 0 <= start < end <= frames:
        raise ValueError(
            f"click {position} covers samples {start} to {end}, outside the file's 0 to {frames}"
        )
    if type(entry["width_samples"]) is not int or entry["width_samples"] != end - start:
        raise ValueError(f"click {position} has an invalid width_samples")
    for key, upper in (("confidence", 1.0), ("residual_rms", math.inf)):
        value = entry[key]
        if not is_finite_number(value) or not 0 <= value <= upper:
            raise ValueError(f"click {position} has an invalid {key}")
    if entry["repair"] not in ("lsar", "cubic", "unrepaired"):
        raise ValueError(f"click {position} has an unknown repair method")


@dataclass(slots=True)
class Click:
    channel: int
    start_sample: int
    end_sample: int
    width_samples: int
    confidence: float
    residual_rms: float
    repair: str  # "lsar" | "cubic" | "unrepaired"


def totals(clicks: list[dict], frames: int) -> dict:
    """The summary block, over emitted click records rather than the dataclasses."""
    repaired = sum(c["width_samples"] for c in clicks if c["repair"] != "unrepaired")
    return {
        "count": len(clicks),
        "samples_repaired": repaired,
        "pct_of_duration": round((repaired / frames * 100.0) if frames else 0.0, 2),
    }


def build(
    *,
    input_path: str,
    sample_rate: int,
    channels: int,
    frames: int,
    clicks: Iterable[Click],
) -> dict:
    emitted = [
        {
            "channel": c.channel,
            "start_sample": c.start_sample,
            "end_sample": c.end_sample,
            "width_samples": c.width_samples,
            "confidence": round(c.confidence, 4),
            "residual_rms": round(c.residual_rms, 8),
            "repair": c.repair,
        }
        for c in sorted(clicks, key=lambda c: (c.start_sample, c.channel))
    ]
    return {
        "input": input_path,
        "sample_rate": sample_rate,
        "channels": channels,
        "duration_s": round(frames / sample_rate, 3) if sample_rate else 0.0,
        "clicks": emitted,
        "totals": totals(emitted, frames),
    }


def write(report: dict, path: str | Path) -> None:
    Path(path).write_text(json.dumps(report, indent=2), encoding="utf-8")
