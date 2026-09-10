"""Render docs/before-after.png from the bundled 78 excerpt.

Needs matplotlib, which the package itself does not:

    pip install matplotlib
    python docs/make_figure.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
import numpy as np
import soundfile as sf

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from grooveclean import cli, detect  # noqa: E402

WINDOW = 2048
HOP = 512
FLOOR_DB = 78.0


def spectrogram(x: np.ndarray) -> np.ndarray:
    """Short-time magnitude in dB, low frequency first."""
    window = np.hanning(WINDOW).astype(np.float32)
    frames = 1 + (x.size - WINDOW) // HOP
    strided = np.lib.stride_tricks.as_strided(
        x, (frames, WINDOW), (x.strides[0] * HOP, x.strides[0]), writeable=False
    )
    mag = np.abs(np.fft.rfft(strided * window, axis=1)).T
    return 20.0 * np.log10(mag + 1e-10)


def panel(ax, x: np.ndarray, rate: int, title: str, ceiling: float | None, top_khz: float) -> float:
    """Draw one spectrogram. All three panels share the first one's dB scale."""
    db = spectrogram(x)
    top = db.max() if ceiling is None else ceiling
    ax.imshow(
        db,
        origin="lower",
        aspect="auto",
        cmap="magma",
        vmin=top - FLOOR_DB,
        vmax=top,
        extent=(0.0, x.size / rate, 0.0, rate / 2000.0),
    )
    ax.set_ylim(0.0, min(top_khz, rate / 2000.0))
    ax.set_title(title, fontsize=10, loc="left")
    ax.set_ylabel("kHz", fontsize=8)
    ax.tick_params(labelsize=8)
    return db.max()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    ap.add_argument("--input", type=Path, default=root / "tests/data/excerpt78.flac")
    ap.add_argument("--out", type=Path, default=root / "docs/before-after.png")
    ap.add_argument("--start", type=float, default=1.0)
    ap.add_argument("--seconds", type=float, default=6.0)
    ap.add_argument("--top-khz", type=float, default=22.05, help="Y axis limit.")
    args = ap.parse_args(argv)

    work = args.out.parent / "_figure"
    work.mkdir(parents=True, exist_ok=True)
    cleaned = work / "cleaned.wav"
    report = cli.clean_file(args.input, cleaned, detector=detect.Detector.load(None, "auto"))

    rate = report["sample_rate"]
    first = int(args.start * rate)
    last = first + int(args.seconds * rate)

    def take(path):
        cut = sf.read(str(path), dtype="float32", always_2d=True)[0][first:last, 0]
        return np.ascontiguousarray(cut)

    before, after = take(args.input), take(cleaned)
    removed = take(cli.sidecars(cleaned)[0])

    fig, axes = plt.subplots(3, 1, figsize=(9.0, 7.5), sharex=True, constrained_layout=True)
    ceiling = panel(axes[0], before, rate, "before", None, args.top_khz)
    panel(axes[1], after, rate, "after", ceiling, args.top_khz)
    panel(axes[2], removed, rate, "removed (the difference file)", ceiling, args.top_khz)
    axes[2].set_xlabel("seconds", fontsize=8)
    fig.suptitle(
        f"{args.input.name}: {report['totals']['count']:,} clicks, "
        f"{report['totals']['pct_of_duration']}% of the side",
        fontsize=11,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=110)

    for path in (cleaned, *cli.sidecars(cleaned)):
        path.unlink(missing_ok=True)
    work.rmdir()
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
