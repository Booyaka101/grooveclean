"""Audition what a run took out, and put back the repairs it got wrong.

Both halves rest on the same guarantee: the cleaned file and its difference file add back up
to the input exactly, so the audio underneath any repair can be recovered without keeping the
source file, and one repair can be undone without touching the rest. On a float file the sum
is exact only to within float32 rounding, which is the same accuracy the run itself had.
"""

from __future__ import annotations

import json
import math
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import io, report
from .repair import METHOD_NAMES, UNREPAIRED

GAP_MS = 400.0  # between excerpts, so a run of them does not sound like one performance
CHUNK_FRAMES = 1 << 20

NEVER_REPAIRED = METHOD_NAMES[UNREPAIRED]

# Descending unless the name says otherwise: the first row is the one worth hearing first.
SORT_KEYS = {
    "removed": lambda c: (-c["residual_rms"], c["start_sample"]),
    "width": lambda c: (-c["width_samples"], c["start_sample"]),
    "doubt": lambda c: (c["confidence"], c["start_sample"]),
    "time": lambda c: c["start_sample"],
}


class ReviewError(Exception):
    """A cleaned file that cannot be reviewed, or a selection that names nothing."""


@dataclass(slots=True)
class Pair:
    """A cleaned file with the difference file and report that were written beside it."""

    cleaned: io.Info
    removed: io.Info
    report: dict

    @property
    def clicks(self) -> list[dict]:
        return self.report["clicks"]


def open_pair(cleaned: str | Path) -> Pair:
    cleaned = Path(cleaned)
    removed_path, report_path = io.sidecars(cleaned)
    missing = [p.name for p in (removed_path, report_path) if not p.exists()]
    if missing:
        raise ReviewError(
            f"{cleaned}: {' and '.join(missing)} "
            f"{'are' if len(missing) > 1 else 'is'} not next to it. Reviewing a run reads all "
            "three files it wrote, so keep them together."
        )
    info, difference = io.probe(cleaned), io.probe(removed_path)
    shape = (info.samplerate, info.channels, info.frames)
    if shape != (difference.samplerate, difference.channels, difference.frames):
        raise ReviewError(
            f"{cleaned} and {removed_path.name} are not the same audio: "
            f"{shape} against {(difference.samplerate, difference.channels, difference.frames)}. "
            "They have to be a pair from one run."
        )
    try:
        built = json.loads(report_path.read_text(encoding="utf-8"))
        clicks = built["clicks"]
        if not isinstance(clicks, list) or built["sample_rate"] != info.samplerate:
            raise KeyError("clicks")
        for position, entry in enumerate(clicks, start=1):
            check_click(entry, position, info)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ReviewError(f"{report_path}: not a report for {cleaned.name} ({exc})") from exc
    return Pair(cleaned=info, removed=difference, report=built)


# What every click record has to carry for a span to be locatable in the audio.
CLICK_FIELDS = ("channel", "start_sample", "end_sample", "width_samples", "confidence",
                "residual_rms", "repair")


def check_click(entry: dict, position: int, info: io.Info) -> None:
    """Reject a record that cannot describe a span of this file, before anything indexes with it.

    A report is a plain JSON file a user can edit, and a bad number in one reaches numpy as an
    index rather than as a complaint.
    """
    if not isinstance(entry, dict) or any(field not in entry for field in CLICK_FIELDS):
        raise ValueError(f"click {position} is missing fields")
    start, end, channel = entry["start_sample"], entry["end_sample"], entry["channel"]
    if not all(isinstance(value, int) for value in (start, end, channel)):
        raise ValueError(f"click {position} has a position that is not a whole number")
    if not 0 <= channel < info.channels:
        raise ValueError(
            f"click {position} is on channel {channel} of a {info.channels}-channel file"
        )
    if not 0 <= start < end <= info.frames:
        raise ValueError(
            f"click {position} covers samples {start} to {end}, outside the file's 0 to "
            f"{info.frames}"
        )


def parse_indices(text: str, total: int) -> set[int]:
    """`3,17,204` or `12-18` or a mix, one-based the way the audit table prints them."""
    chosen: set[int] = set()
    for piece in text.replace(" ", "").split(","):
        if not piece:
            continue
        low, dash, high = piece.partition("-")
        try:
            first = int(low)
            last = int(high) if dash else first
        except ValueError:
            raise ReviewError(f"{piece!r} is not a click number or a range like 12-18") from None
        if first < 1 or last > total or last < first:
            raise ReviewError(f"{piece} is outside the report's 1-{total}")
        chosen.update(range(first, last + 1))
    return chosen


def parse_time(text: str) -> float:
    """Seconds from `92`, `1:32` or `1:32.415`, the way a player writes a position."""
    minutes, _, seconds = text.strip().rpartition(":")
    try:
        return (float(minutes) * 60.0 if minutes else 0.0) + float(seconds)
    except ValueError:
        raise ReviewError(f"{text!r} is not a time like 1:32 or 92") from None


def parse_span(text: str, rate: int) -> tuple[int, int]:
    """`1:32-1:40` as a pair of sample positions."""
    first, _, last = text.partition("-")
    if not last:
        raise ReviewError(f"{text!r} is not a stretch of the side, like 1:32-1:40")
    start, end = parse_time(first), parse_time(last)
    if end <= start:
        raise ReviewError(f"{text}: the second time has to come after the first")
    return int(start * rate), int(end * rate)


def select(
    clicks: list[dict],
    *,
    rate: int,
    indices: str | None = None,
    between: str | None = None,
    wider_than_ms: float | None = None,
    confidence_below: float | None = None,
) -> list[int]:
    """Positions into `clicks` from any mix of the selectors, or all of them when given none.

    Spans the run left unrepaired are dropped: there is nothing under them to hear or restore.
    """
    asked = (indices, between, wider_than_ms, confidence_below)
    if all(value is None for value in asked):
        chosen = set(range(len(clicks)))
    else:
        chosen = {i - 1 for i in parse_indices(indices, len(clicks))} if indices else set()
        if between is not None:
            start, end = parse_span(between, rate)
            chosen |= {
                i
                for i, c in enumerate(clicks)
                if c["end_sample"] > start and c["start_sample"] < end
            }
        if wider_than_ms is not None:
            limit = wider_than_ms * 1e-3 * rate
            chosen |= {i for i, c in enumerate(clicks) if c["width_samples"] > limit}
        if confidence_below is not None:
            chosen |= {i for i, c in enumerate(clicks) if c["confidence"] < confidence_below}
    return sorted(i for i in chosen if clicks[i]["repair"] != NEVER_REPAIRED)


def rank(clicks: list[dict], chosen: Iterable[int], key: str, top: int) -> list[int]:
    ordered = sorted(chosen, key=lambda i: SORT_KEYS[key](clicks[i]))
    return ordered[:top] if top > 0 else ordered


def windows(
    clicks: list[dict], chosen: list[int], context: int, frames: int
) -> list[tuple[int, int, list[int]]]:
    """Merge the chosen spans into excerpt bounds, so two clicks a moment apart play once."""
    bounds = sorted(
        (
            max(0, clicks[i]["start_sample"] - context),
            min(frames, clicks[i]["end_sample"] + context),
            i,
        )
        for i in chosen
    )
    merged: list[tuple[int, int, list[int]]] = []
    for low, high, index in bounds:
        if merged and low <= merged[-1][1]:
            last = merged[-1]
            merged[-1] = (last[0], max(last[1], high), [*last[2], index])
        else:
            merged.append((low, high, [index]))
    return merged


def audit(
    pair: Pair, chosen: list[int], before_path: Path, after_path: Path, context_ms: float
) -> list[tuple[int, int]]:
    """Write the two aligned excerpt files. Returns (excerpt number, click position) pairs."""
    info = pair.cleaned
    context = int(round(context_ms * 1e-3 * info.samplerate))
    gap = np.zeros((int(round(GAP_MS * 1e-3 * info.samplerate)), info.channels))
    cut = windows(pair.clicks, chosen, context, info.frames)
    before_path.parent.mkdir(parents=True, exist_ok=True)

    with (
        io.unlink_on_failure((before_path, after_path)),
        io.open_read(info) as clean_fh,
        io.open_read(pair.removed) as removed_fh,
        io.Writer(before_path, info) as before,
        io.Writer(after_path, info) as after,
    ):
        for number, (low, high, _) in enumerate(cut):
            if number:
                before.write(gap)
                after.write(gap)
            repaired = io.read_at(clean_fh, low, high - low, info)
            before.write(repaired + io.read_at(removed_fh, low, high - low, pair.removed))
            after.write(repaired)
    return [(n + 1, i) for n, (_, _, members) in enumerate(cut) for i in members]


def revert(pair: Pair, chosen: list[int], output: Path) -> dict:
    """Add the chosen repairs back and write a fresh cleaned/difference/report set."""
    info = pair.cleaned
    picked = [pair.clicks[i] for i in chosen]
    starts = np.array([c["start_sample"] for c in picked], dtype=np.int64)
    ends = np.array([c["end_sample"] for c in picked], dtype=np.int64)
    channels = np.array([c["channel"] for c in picked], dtype=np.int64)

    removed_path, report_path = io.sidecars(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    io.format_for(output, info)
    with (
        io.unlink_on_failure((output, removed_path)),
        io.open_read(info) as clean_fh,
        io.open_read(pair.removed) as removed_fh,
        io.Writer(output, info) as out_fh,
        io.Writer(removed_path, info) as rest_fh,
    ):
        for start in range(0, info.frames, CHUNK_FRAMES):
            count = min(CHUNK_FRAMES, info.frames - start)
            keep = io.read_at(clean_fh, start, count, info)
            difference = io.read_at(removed_fh, start, count, pair.removed)
            for i in np.flatnonzero((ends > start) & (starts < start + count)):
                low = max(int(starts[i]), start) - start
                high = min(int(ends[i]), start + count) - start
                keep[low:high, channels[i]] += difference[low:high, channels[i]]
                difference[low:high, channels[i]] = 0.0
            out_fh.write(keep)
            rest_fh.write(difference)

    dropped = set(chosen)
    kept = [c for i, c in enumerate(pair.clicks) if i not in dropped]
    built = dict(pair.report, clicks=kept, totals=report.totals(kept, info.frames))
    report.write(built, report_path)
    return built


def plural(count: int, word: str) -> str:
    return f"{count:,} {word}{'' if count == 1 else 's'}"


def timestamp(sample: int, rate: int) -> str:
    """m:ss.mmm from the start of the file, which is what a player's counter shows."""
    minutes, rest = divmod(sample * 1000 // rate, 60_000)
    return f"{minutes}:{rest // 1000:02d}.{rest % 1000:03d}"


def dbfs(rms: float) -> str:
    return f"{20.0 * math.log10(rms):.1f}" if rms > 0.0 else "-"


def channel_name(channel: int, channels: int) -> str:
    return ("L", "R")[channel] if channels == 2 else str(channel)
