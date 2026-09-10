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

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SOFT = "#52514e"
BEFORE = "#2a78d6"
AFTER = "#eb6834"
REMOVED = "#4a3aa7"
ZOOM_MS = 4.0


def style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "axes.edgecolor": "#d6d5d0",
            "axes.labelcolor": INK_SOFT,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "axes.titlecolor": INK,
            "text.color": INK,
            "xtick.color": INK_SOFT,
            "ytick.color": INK_SOFT,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "font.size": 9,
            "legend.frameon": False,
            "legend.fontsize": 8,
        }
    )


def spectrogram(x: np.ndarray) -> np.ndarray:
    """Short-time magnitude in dB, low frequency first."""
    window = np.hanning(WINDOW).astype(np.float32)
    frames = 1 + (x.size - WINDOW) // HOP
    strided = np.lib.stride_tricks.as_strided(
        x, (frames, WINDOW), (x.strides[0] * HOP, x.strides[0]), writeable=False
    )
    mag = np.abs(np.fft.rfft(strided * window, axis=1)).T
    return 20.0 * np.log10(mag + 1e-10)


def panel(ax, x: np.ndarray, rate: int, title: str, ceiling: float | None, top_khz: float):
    """Draw one spectrogram. All three panels share the first one's dB scale."""
    db = spectrogram(x)
    top = db.max() if ceiling is None else ceiling
    image = ax.imshow(
        db,
        origin="lower",
        aspect="auto",
        cmap="magma",
        vmin=top - FLOOR_DB,
        vmax=top,
        extent=(0.0, x.size / rate, 0.0, rate / 2000.0),
    )
    ax.set_ylim(0.0, min(top_khz, rate / 2000.0))
    ax.set_title(title, loc="left", pad=5)
    ax.set_ylabel("kHz")
    for spine in ax.spines.values():
        spine.set_visible(False)
    return image, db.max()


def loudest_click(report: dict, rate: int, margin: int) -> dict:
    """The click with the most energy in it, far enough inside the file to zoom on."""
    inside = [
        c
        for c in report["clicks"]
        if c["channel"] == 0 and c["start_sample"] > margin and c["end_sample"] < margin * 40
    ]
    pool = inside or [c for c in report["clicks"] if c["channel"] == 0]
    return max(pool, key=lambda c: c["residual_rms"])


def zoom(ax, before: np.ndarray, after: np.ndarray, rate: int, click: dict) -> None:
    """One real click at sample resolution, damaged and repaired on the same axes."""
    half = int(ZOOM_MS * 1e-3 * rate / 2)
    middle = (click["start_sample"] + click["end_sample"]) // 2
    lo, hi = max(0, middle - half), middle + half
    t = (np.arange(lo, hi) - middle) / rate * 1e3

    ax.axvspan(
        (click["start_sample"] - middle) / rate * 1e3,
        (click["end_sample"] - middle) / rate * 1e3,
        color="#e9e8e3",
        lw=0,
        zorder=0,
    )
    ax.plot(t, before[lo:hi], color=BEFORE, lw=2.0, label="before", zorder=2)
    ax.plot(t, after[lo:hi], color=AFTER, lw=2.0, label="after", zorder=3)
    ax.axhline(0.0, color="#d6d5d0", lw=1.0, zorder=1)

    peak = int(np.argmax(np.abs(before[lo:hi])))
    ax.annotate(
        "before",
        (t[peak], before[lo + peak]),
        textcoords="offset points",
        xytext=(8, 2),
        color=BEFORE,
        fontsize=9,
        fontweight="bold",
    )
    ax.annotate(
        "after",
        ((click["end_sample"] - middle) / rate * 1e3, after[click["end_sample"] - lo]),
        textcoords="offset points",
        xytext=(10, -12),
        color=AFTER,
        fontsize=9,
        fontweight="bold",
    )
    width_ms = click["width_samples"] / rate * 1e3
    ax.set_title(
        f"one click at sample resolution: {click['width_samples']} samples, {width_ms:.2f} ms, "
        f"filled by AR interpolation",
        loc="left",
        pad=5,
    )
    ax.set_xlabel("milliseconds either side of the click")
    ax.set_ylabel("amplitude")
    ax.set_xlim(t[0], t[-1])
    ax.legend(loc="lower right", ncol=2)
    ax.grid(axis="y", color="#eceae4", lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def difference(ax, removed: np.ndarray, rate: int, seconds: float) -> None:
    """The whole difference file end to end. Isolated spikes on a flat zero line, or a bug."""
    t = np.arange(removed.size) / rate
    ax.axhline(0.0, color="#d6d5d0", lw=1.0)
    ax.plot(t, removed, color=REMOVED, lw=0.7)
    ax.set_title(
        "removed, the difference file: every spike is one click, the flat line is untouched audio",
        loc="left",
        pad=5,
    )
    ax.set_ylabel("amplitude")
    ax.set_xlabel("seconds into the excerpt")
    ax.set_xlim(0.0, seconds)
    ax.grid(axis="y", color="#eceae4", lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    ap.add_argument("--input", type=Path, default=root / "tests/data/excerpt78.flac")
    ap.add_argument("--out", type=Path, default=root / "docs/before-after.png")
    ap.add_argument("--start", type=float, default=1.0)
    ap.add_argument("--seconds", type=float, default=3.0)
    ap.add_argument("--top-khz", type=float, default=22.05, help="Y axis limit.")
    args = ap.parse_args(argv)

    work = args.out.parent / "_figure"
    work.mkdir(parents=True, exist_ok=True)
    cleaned = work / "cleaned.wav"
    report = cli.clean_file(args.input, cleaned, detector=detect.Detector.load(None, "auto"))

    rate = report["sample_rate"]
    first = int(args.start * rate)
    last = first + int(args.seconds * rate)

    def take(path, lo=first, hi=last):
        cut = sf.read(str(path), dtype="float32", always_2d=True)[0][lo:hi, 0]
        return np.ascontiguousarray(cut)

    before, after = take(args.input), take(cleaned)
    removed = take(cli.sidecars(cleaned)[0])
    whole_before = take(args.input, 0, None)
    whole_after = take(cleaned, 0, None)

    style()
    fig, axes = plt.subplots(
        4,
        1,
        figsize=(10.0, 9.6),
        constrained_layout=True,
        gridspec_kw={"height_ratios": [1.3, 1.0, 1.0, 0.85]},
    )
    zoom(axes[0], whole_before, whole_after, rate, loudest_click(report, rate, 4096))
    image, ceiling = panel(axes[1], before, rate, "before", None, args.top_khz)
    panel(axes[2], after, rate, "after", ceiling, args.top_khz)
    difference(axes[3], removed, rate, args.seconds)
    axes[1].tick_params(labelbottom=False)

    bar = fig.colorbar(image, ax=list(axes[1:3]), pad=0.012, aspect=28)
    bar.set_label("dB relative to the loudest bin", fontsize=8)
    bar.ax.tick_params(labelsize=8)
    bar.outline.set_visible(False)

    fig.suptitle(
        f"{args.input.name}, a 1917 acoustic 78: "
        f"{report['totals']['count']:,} clicks removed, "
        f"{report['totals']['pct_of_duration']}% of the excerpt repaired",
        fontsize=12,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=110, facecolor=SURFACE)

    for path in (cleaned, *cli.sidecars(cleaned)):
        path.unlink(missing_ok=True)
    work.rmdir()
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
