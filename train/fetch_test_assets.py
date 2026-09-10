"""Cut the public-domain audio excerpts the test suite is pinned to, and record where from.

The excerpts themselves are checked in so the tests run offline. This script exists so anyone
can regenerate them, and so the provenance in tests/data/ASSETS.json is produced rather than
typed. Nothing here runs during a normal build or test.

    python train/fetch_test_assets.py
    python train/fetch_test_assets.py --golden   # after training, refresh the golden count
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _ia  # noqa: E402
from grooveclean import cli, detect  # noqa: E402

HEAD_BYTES = 30 << 20
SECONDS = 10.0

ASSETS = [
    {
        "name": "excerpt78",
        "identifier": (
            "78_the-stars-and-stripes-forever-march_"
            "imperial-marimba-band-j-p-sousa_gbia0549589a"
        ),
        "start": 40.0,
        "why": "1917 acoustic 78, in the public domain in the US. The golden click count.",
    },
    {
        "name": "clean_excerpt",
        "identifier": "hr010",
        "start": 60.0,
        "why": "netlabels release under a Creative Commons public domain dedication.",
    },
]


def specs(manifest_path: Path) -> list[dict]:
    """The built-in list, with anything ASSETS.json already pins taking precedence.

    train/pick_clean_excerpt.py rewrites the clean entry, so the manifest is the record of
    what is checked in and re-running this script has to reproduce that rather than the
    original guess.
    """
    if not manifest_path.exists():
        return ASSETS
    pinned = {
        Path(asset["file"]).stem: {
            "name": Path(asset["file"]).stem,
            "identifier": asset["identifier"],
            "start": asset["start_s"],
            "why": asset["why"],
        }
        for asset in json.loads(manifest_path.read_text(encoding="utf-8"))["assets"]
    }
    return [pinned.get(spec["name"], spec) for spec in ASSETS]


def cut(spec: dict, out_dir: Path, work_dir: Path) -> dict:
    meta = _ia.metadata(spec["identifier"])
    files = [f for f in _ia.flac_files(meta) if f["size"] > 0]
    if not files:
        raise _ia.HarvestError(f"{spec['identifier']}: no FLAC in item")
    pick = min(files, key=lambda f: f["size"])

    work_dir.mkdir(parents=True, exist_ok=True)
    path = work_dir / f"{spec['name']}.flac"
    try:
        _ia.download(spec["identifier"], pick["name"], path, max_bytes=HEAD_BYTES)
        with sf.SoundFile(str(path)) as fh:
            rate, subtype = fh.samplerate, fh.subtype
            fh.seek(int(spec["start"] * rate))
            data = fh.read(int(SECONDS * rate), dtype="float64", always_2d=True)
    finally:
        path.unlink(missing_ok=True)
    if data.shape[0] < int(SECONDS * rate):
        raise _ia.HarvestError(
            f"{spec['identifier']}: only {data.shape[0] / rate:.1f} s available at "
            f"{spec['start']:.0f} s, fetch more than {HEAD_BYTES >> 20} MB"
        )

    target = out_dir / f"{spec['name']}.flac"
    out_dir.mkdir(parents=True, exist_ok=True)
    sf.write(str(target), data, rate, subtype=subtype if subtype != "PCM_32" else "PCM_24")
    info = meta.get("metadata", {})
    return {
        "file": target.name,
        "identifier": spec["identifier"],
        "source_file": pick["name"],
        "start_s": spec["start"],
        "seconds": SECONDS,
        "sample_rate": rate,
        "channels": int(data.shape[1]),
        "bytes": target.stat().st_size,
        "peak_dbfs": round(20.0 * float(np.log10(max(1e-12, np.abs(data).max()))), 2),
        "title": info.get("title"),
        "creator": info.get("creator"),
        "date": info.get("date"),
        "licenseurl": info.get("licenseurl"),
        "why": spec["why"],
    }


def golden(data_dir: Path) -> dict:
    """Re-run the shipped detector over the 78 excerpt and record what it found."""
    detector = detect.Detector.load(None, "auto")
    out = data_dir / ".golden" / "out.wav"
    built = cli.clean_file(data_dir / "excerpt78.flac", out, detector=detector)
    for path in (out, *cli.sidecars(out)):
        path.unlink(missing_ok=True)
    out.parent.rmdir()
    return {
        "clicks": built["totals"]["count"],
        "samples_repaired": built["totals"]["samples_repaired"],
        "pct_of_duration": built["totals"]["pct_of_duration"],
        "tolerance": 0.02,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--out", type=Path, default=Path("tests/data"))
    ap.add_argument("--work", type=Path, default=Path("corpus/.work-assets"))
    ap.add_argument("--golden", action="store_true", help="only refresh the golden click count")
    args = ap.parse_args(argv)

    manifest_path = args.out / "ASSETS.json"
    if args.golden:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"assets": []}
        for spec in specs(manifest_path):
            try:
                entry = cut(spec, args.out, args.work)
            except _ia.HarvestError as exc:
                print(f"{spec['name']}: {exc}", file=sys.stderr)
                return 2
            manifest["assets"].append(entry)
            print(
                f"{entry['file']}: {entry['sample_rate']} Hz {entry['channels']}ch "
                f"{entry['bytes'] / 2**20:.1f} MB  peak {entry['peak_dbfs']} dBFS",
                flush=True,
            )

    if detect.WEIGHTS_PATH.exists():
        manifest["golden"] = golden(args.out)
        print(f"golden: {manifest['golden']}")
    else:
        print("no detector weights yet, skipping the golden count", file=sys.stderr)

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
