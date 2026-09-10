"""Run Needledropper's Declicker over a folder, via the headless bridge.

The bridge (nd_cli) is a small main() over that project's src/dsp, which is JUCE-free
and links standalone. It mirrors DetectionThread::run and ProcessingThread's repair
path, including the reverse pass the project's README recommends, at the app's shipped
defaults. That code is AGPL and is not vendored here; build it separately.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import time
from pathlib import Path

import numpy as np
import soundfile as sf


def run(exe: Path, src: Path, dst: Path, sensitivity: float, crackle: float,
        reverse: bool) -> tuple[int, float]:
    x, rate = sf.read(str(src), dtype="float64", always_2d=True)
    tmp_in, tmp_out = dst.with_suffix(".in.raw"), dst.with_suffix(".out.raw")
    x.astype("<f8").tofile(tmp_in)
    started = time.monotonic()
    proc = subprocess.run(
        [str(exe), str(tmp_in), str(tmp_out), str(x.shape[0]), str(x.shape[1]),
         str(rate), str(sensitivity), str(crackle), "1" if reverse else "0"],
        capture_output=True, text=True, check=True)
    elapsed = time.monotonic() - started
    y = np.fromfile(tmp_out, dtype="<f8").reshape(x.shape)
    sf.write(str(dst), y, rate, subtype="PCM_16")
    tmp_in.unlink()
    tmp_out.unlink()
    found = re.search(r"clicks_repaired=(\d+)", proc.stderr)
    return int(found.group(1)) if found else -1, elapsed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path)
    ap.add_argument("--exe", type=Path, default=Path("D:/tmp/bakeoff/nd_cli.exe"))
    ap.add_argument("--sensitivity", type=float, default=30.0, help="app default")
    ap.add_argument("--crackle", type=float, default=0.0, help="app default")
    ap.add_argument("--no-reverse", action="store_true")
    a = ap.parse_args(argv)

    a.dst.mkdir(parents=True, exist_ok=True)
    total = 0.0
    for src in sorted(a.src.glob("*.wav")):
        repaired, elapsed = run(a.exe, src, a.dst / src.name, a.sensitivity,
                                a.crackle, not a.no_reverse)
        total += elapsed
        print(f"{src.name}: {repaired:,} repaired in {elapsed:.1f}s")
    print(f"total {total:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
