"""Render docs/demo/*.mp3 from the bundled 78 excerpt.

Ten seconds of a 1917 acoustic transfer, before and after, plus the difference file so you
can hear exactly what was taken out.

    python docs/make_demo.py

Needs a libsndfile built with MP3 support, which the soundfile wheels have had since 0.12.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from grooveclean import cli, detect  # noqa: E402

DEMO_RATE = 44100
BITRATE_MODE = "CONSTANT"


def to_demo_rate(x: np.ndarray, rate: int) -> np.ndarray:
    """Band-limit and resample to 44.1 kHz, the highest rate MP3 encodes without quality loss."""
    if rate == DEMO_RATE:
        return x
    n_out = round(x.shape[0] * DEMO_RATE / rate)
    t = torch.from_numpy(np.ascontiguousarray(x.T))
    return detect.resample(t, n_out).numpy().T


def write(path: Path, x: np.ndarray, quality: float) -> None:
    with sf.SoundFile(
        str(path),
        "w",
        samplerate=DEMO_RATE,
        channels=x.shape[1],
        format="MP3",
        subtype="MPEG_LAYER_III",
        compression_level=quality,
        bitrate_mode=BITRATE_MODE,
    ) as out:
        out.write(x)
    print(f"  {path.name}  {path.stat().st_size / 1024:.0f} KB  peak {peak_dbfs(x):+.1f} dBFS")


def peak_dbfs(x: np.ndarray) -> float:
    peak = float(np.max(np.abs(x)))
    return -np.inf if peak == 0.0 else 20.0 * np.log10(peak)


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, default=root / "tests/data/excerpt78.flac")
    ap.add_argument("--out-dir", type=Path, default=root / "docs/demo")
    ap.add_argument("--quality", type=float, default=0.2, help="0 is best, 1 is smallest.")
    args = ap.parse_args(argv)

    if "MP3" not in sf.available_formats():
        print("this libsndfile cannot write MP3; upgrade soundfile", file=sys.stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    work = args.out_dir / "_work"
    work.mkdir(exist_ok=True)
    cleaned = work / "cleaned.wav"
    report = cli.clean_file(args.input, cleaned, detector=detect.Detector.load(None, "auto"))
    rate = report["sample_rate"]

    def take(path: Path) -> np.ndarray:
        return to_demo_rate(sf.read(str(path), dtype="float32", always_2d=True)[0], rate)

    print(f"{report['totals']['count']:,} clicks, {report['totals']['pct_of_duration']}% repaired")
    write(args.out_dir / "1-before.mp3", take(args.input), args.quality)
    write(args.out_dir / "2-after.mp3", take(cleaned), args.quality)
    write(args.out_dir / "3-removed.mp3", take(cli.sidecars(cleaned)[0]), args.quality)

    for path in (cleaned, *cli.sidecars(cleaned)):
        path.unlink(missing_ok=True)
    work.rmdir()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
