"""Harvest click-free music from the Internet Archive's netlabels collection.

These are born-digital releases under Creative Commons terms, so they carry no surface noise
and can be used as the clean side of a training pair. Some of them are vinyl rips or glitch
records that already contain the thing this detector is supposed to find, so every candidate
is run through an impulse detector of its own and rejected if it fires too often. Percussive
material is deliberately kept: the model has to see snare hits labelled as not-a-click.

Clips are stored as 44.1 kHz 16-bit FLAC, which is what a consumer release is anyway.

The held-out evaluation file is checked into the repo, so it can only be built from items
whose licence allows that; --redistributable restricts the search to those.

    python train/harvest_clean.py --items 300 --out corpus/clean
    python train/harvest_clean.py --items 400 --redistributable
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _ia  # noqa: E402
from grooveclean import detect  # noqa: E402

# Archive.org's licenceurl field, restricted to the two families that can be mixed into an
# evaluation file and checked into an MIT repo.
REDISTRIBUTABLE_ONLY = r"AND (licenseurl:*publicdomain* OR licenseurl:*licenses\/by\/*)"

COLLECTION = _ia.Collection(
    query='collection:"netlabels" AND format:"Flac"',
    rows=2000,
    fields=["identifier", "title", "creator", "licenseurl"],
    label="clean",
    banner="netlabels+FLAC",
)
FIELDS = COLLECTION.fields

SKIP_SECONDS = 5.0  # past the fade-in and the label ident
CLIP_SECONDS = 60.0
MIN_SECONDS = 20.0

IMPULSE_GATE = 12.0
EDGE_GATE = 3.0
MAX_IMPULSE_WIDTH = 8  # samples; wider than this is a musical transient, not a tick
MAX_IMPULSES_PER_S = 5.0

MIN_PEAK = 0.01
MIN_RMS_DBFS = -50.0

WHOLE_FILE_BYTES = 20 << 20
HEAD_BYTES = 12 << 20


def impulse_rate(x: np.ndarray, rate: int) -> float:
    """Narrow impulses per second, ignoring anything sitting on a clipped run."""
    impulsive = detect.impulsiveness(torch.from_numpy(x.astype(np.float32)), rate).numpy()
    impulsive[detect.clipped(x)] = 0.0
    starts, ends, _ = detect.hysteresis(impulsive, IMPULSE_GATE, EDGE_GATE)
    width = ends - starts
    return float(np.count_nonzero((width >= 1) & (width <= MAX_IMPULSE_WIDTH))) / (x.size / rate)


def usable(data: np.ndarray, rate: int) -> str:
    """Empty string if the clip can be used, otherwise the reason it cannot."""
    if data.shape[0] < MIN_SECONDS * rate:
        return f"only {data.shape[0] / rate:.1f} s decoded"
    peak = float(np.abs(data).max())
    if peak < MIN_PEAK:
        return "silent or near-silent"
    level = 20.0 * np.log10(max(1e-12, float(np.sqrt(np.mean(data.astype(np.float64) ** 2)))))
    if level < MIN_RMS_DBFS:
        return f"level {level:.0f} dBFS is too low to be a release"
    worst = max(
        impulse_rate(np.ascontiguousarray(data[:, ch]), rate) for ch in range(data.shape[1])
    )
    if worst > MAX_IMPULSES_PER_S:
        return f"{worst:.1f} impulses/s, already clicky"
    return ""


def harvest_one(doc: dict, out_dir: Path, work_dir: Path) -> _ia.Outcome:
    ident = doc["identifier"]
    target = out_dir / f"{ident}.flac"
    if target.exists():
        return _ia.Outcome(ident, "ok", "cached", _provenance(doc))
    try:
        data, info = _ia.fetch_audio(
            ident,
            work_dir,
            whole_below=WHOLE_FILE_BYTES,
            head_bytes=HEAD_BYTES,
            rate_out=detect.ANALYSIS_RATE,
        )
        rate = detect.ANALYSIS_RATE
        clip = data[int(SKIP_SECONDS * rate) : int((SKIP_SECONDS + CLIP_SECONDS) * rate)]
        clip = clip[:, : min(2, clip.shape[1])]
        reason = usable(clip, rate)
        if reason:
            return _ia.Outcome(ident, "skip", reason)
        sf.write(str(target), clip, rate, subtype="PCM_16")
        return _ia.Outcome(
            ident,
            "ok",
            f"{clip.shape[0] / rate:.0f}s {clip.shape[1]}ch",
            {"seconds": round(clip.shape[0] / rate, 2), **_provenance(doc), **info},
        )
    except Exception as exc:
        return _ia.Outcome(ident, "error", f"{type(exc).__name__}: {exc}")


def _provenance(doc: dict) -> dict:
    return {field: doc.get(field) for field in FIELDS if field != "identifier"}


def main(argv: list[str] | None = None) -> int:
    ap = _ia.build_parser(__doc__, items=300, out="corpus/clean")
    ap.add_argument(
        "--redistributable",
        action="store_true",
        help="only public domain and CC-BY items, which are the ones the evaluation mix "
        "can be built from",
    )
    args = ap.parse_args(argv)
    collection = COLLECTION
    if args.redistributable:
        collection = replace(collection, query=f"{COLLECTION.query} {REDISTRIBUTABLE_ONLY}")
    return _ia.harvest(collection, args, lambda d: harvest_one(d, args.out, args.work))


if __name__ == "__main__":
    raise SystemExit(_ia.run_cli(main))
