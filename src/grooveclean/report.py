"""JSON report emission for a cleaning run."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Click:
    channel: int
    start_sample: int
    end_sample: int
    width_samples: int
    confidence: float
    residual_rms: float
    repair: str  # "lsar" | "cubic" | "unrepaired"


def build(
    *,
    input_path: str,
    sample_rate: int,
    channels: int,
    frames: int,
    clicks: Iterable[Click],
) -> dict:
    clicks = sorted(clicks, key=lambda c: (c.start_sample, c.channel))
    repaired = sum(c.width_samples for c in clicks if c.repair != "unrepaired")
    pct = (repaired / frames * 100.0) if frames else 0.0
    return {
        "input": input_path,
        "sample_rate": sample_rate,
        "channels": channels,
        "duration_s": round(frames / sample_rate, 3) if sample_rate else 0.0,
        "clicks": [
            {
                "channel": c.channel,
                "start_sample": c.start_sample,
                "end_sample": c.end_sample,
                "width_samples": c.width_samples,
                "confidence": round(c.confidence, 4),
                "residual_rms": round(c.residual_rms, 8),
                "repair": c.repair,
            }
            for c in clicks
        ],
        "totals": {
            "count": len(clicks),
            "samples_repaired": repaired,
            "pct_of_duration": round(pct, 2),
        },
    }


def write(report: dict, path: str | Path) -> None:
    Path(path).write_text(json.dumps(report, indent=2), encoding="utf-8")
