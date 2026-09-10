"""Choose the click-free excerpt the clean-audio guard is pinned to, and cut it.

The guard test asserts that a real commercial release comes out with a silent difference file.
That only means something if the excerpt really has no impulses in it, so candidates are
screened with the plain second-difference statistic from the harvester, not with the network
that is under test: a window qualifies only if that screen finds zero narrow impulses in it.
Everything that survives is then run through the shipped detector and reported, so the number
of screened windows it leaves alone is visible rather than implied by the one that got picked.

Candidates come from the harvested clean corpus, restricted to public domain and CC-BY items
because the excerpt is checked into an MIT repo.

    python train/pick_clean_excerpt.py
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

import fetch_test_assets  # noqa: E402
import harvest_clean  # noqa: E402
import mix  # noqa: E402
from grooveclean import cli, detect  # noqa: E402

WINDOW_S = fetch_test_assets.SECONDS
STEP_S = 5.0
SILENT_DBFS = -80.0
WHY = "netlabels release, screened for impulses window by window before being pinned."


def quiet_windows(path: Path) -> list[float]:
    """Offsets into the clip, in seconds, whose next ten seconds hold no narrow impulse."""
    data, rate = sf.read(str(path), dtype="float32", always_2d=True)
    span = int(WINDOW_S * rate)
    out = []
    for start in range(0, max(0, data.shape[0] - span) + 1, int(STEP_S * rate)):
        block = data[start : start + span]
        worst = max(
            harvest_clean.impulse_rate(np.ascontiguousarray(block[:, ch]), rate)
            for ch in range(block.shape[1])
        )
        if worst == 0.0:
            out.append(start / rate)
    return out


def removed_peak_dbfs(source: Path, work: Path, detector: detect.Detector) -> float:
    """Peak of the difference file, in dBFS, after cleaning `source`."""
    out = work / "probe.wav"
    cli.clean_file(source, out, detector=detector)
    removed = cli.sidecars(out)[0]
    data, _ = sf.read(str(removed), dtype="float64", always_2d=True)
    peak = float(np.abs(data).max()) if data.size else 0.0
    for path in (out, *cli.sidecars(out)):
        path.unlink(missing_ok=True)
    return 20.0 * float(np.log10(peak)) if peak > 0.0 else float("-inf")


def candidates(clean_dir: Path) -> list[tuple[str, float]]:
    """One quiet window per redistributable item, so a run of tries spans that many releases.

    A single release can have a dozen quiet windows in it. Cutting twelve of those would
    re-download the same track twelve times and say nothing about how often the detector
    leaves an arbitrary release alone.
    """
    manifest = json.loads((clean_dir / "manifest.json").read_text(encoding="utf-8"))
    found = []
    for item in manifest["items"]:
        licence = item.get("licenseurl") or ""
        clip = clean_dir / f"{item['identifier']}.flac"
        if not any(tag in licence for tag in mix.REDISTRIBUTABLE) or not clip.exists():
            continue
        offsets = quiet_windows(clip)
        if offsets:
            found.append((item["identifier"], offsets[len(offsets) // 2]))
    return sorted(found)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--clean", type=Path, default=Path("corpus/clean"))
    ap.add_argument("--out", type=Path, default=Path("tests/data"))
    ap.add_argument("--work", type=Path, default=Path("corpus/.work-assets"))
    ap.add_argument("--tries", type=int, default=12, help="how many windows to actually cut")
    args = ap.parse_args(argv)

    found = candidates(args.clean)
    if not found:
        print(
            f"{args.clean}: no redistributable clip has a ten second window with no impulses",
            file=sys.stderr,
        )
        return 2
    print(f"{len(found)} items have a ten second window with nothing impulsive in it", flush=True)

    detector = detect.Detector.load(None, "auto")
    args.work.mkdir(parents=True, exist_ok=True)
    probe = args.work / "candidate.flac"
    silent, entry = 0, None
    for ident, offset in found[: args.tries]:
        spec = {
            "name": "candidate",
            "identifier": ident,
            "start": round(harvest_clean.SKIP_SECONDS + offset, 2),
            "why": WHY,
        }
        try:
            cut = fetch_test_assets.cut(spec, args.work, args.work)
        except Exception as exc:  # network, missing file, too short: try the next window
            print(f"{ident} @{spec['start']}s: {type(exc).__name__}: {exc}", flush=True)
            continue
        peak = removed_peak_dbfs(probe, args.work, detector)
        print(f"{ident} @{spec['start']}s: removed peak {peak:.1f} dBFS", flush=True)
        if peak < SILENT_DBFS:
            silent += 1
            if entry is None:
                entry = cut
                probe.replace(args.out / "clean_excerpt.flac")
        probe.unlink(missing_ok=True)

    print(f"the shipped detector left {silent} of the cut windows alone")
    if entry is None:
        print(
            "none of them came out silent; the detector or the screen needs looking at",
            file=sys.stderr,
        )
        return 1

    entry["file"] = "clean_excerpt.flac"
    entry["bytes"] = (args.out / "clean_excerpt.flac").stat().st_size
    manifest_path = args.out / "ASSETS.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["assets"] = [a for a in manifest["assets"] if a["file"] != "clean_excerpt.flac"]
    manifest["assets"].append(entry)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"pinned {entry['identifier']} at {entry['start_s']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
