"""Compare declickers on real transfers, where there is no ground truth to score against.

Everything here is a proxy. What each tool took out is `in - out`, and the question is
whether that residue looks like damage or like music. A tick is broadband, so its residue
has a flat spectrum; a swallowed cymbal or a bowed note does not. None of this proves a
tool is right, it only shows what it decided to remove.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train"))

from metrics import runs  # noqa: E402
from score import MERGE_GAP, merge  # noqa: E402


def occupied_bins(x: np.ndarray, rate: int) -> float:
    """Fraction of the rfft band holding 99% of the file's energy.

    These are 78s at 96 kHz with nothing above about 8 kHz. Flatness over the whole band
    would mostly measure how much empty top the transfer has, and would reward a tool whose
    interpolation rings wideband, so every tool is judged on the band the music occupies.
    """
    power = np.abs(np.fft.rfft(x[: 1 << 20])) ** 2
    return float(np.searchsorted(np.cumsum(power) / power.sum(), 0.99) + 1) / power.size


def flatness(x: np.ndarray, upto: float) -> float:
    """Spectral flatness over the occupied band: 1 for broadband, towards 0 for tonal."""
    power = np.abs(np.fft.rfft(x * np.hanning(x.size))) ** 2 + 1e-20
    power = power[: max(4, int(round(upto * power.size)))]
    return float(np.exp(np.log(power).mean()) / power.mean())


def measure(src: Path, got: Path, upto: float) -> dict:
    a = sf.read(str(src), dtype="int16", always_2d=True)[0].astype(np.float64)
    b = sf.read(str(got), dtype="int16", always_2d=True)[0].astype(np.float64)
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    took = a - b
    touched = (took != 0).any(axis=1)
    rate = sf.info(str(src)).samplerate

    starts, ends = merge(*runs(touched), MERGE_GAP)
    flats = []
    for lo, hi in zip(starts, ends, strict=True):
        pad = max(16, hi - lo)
        lo2, hi2 = max(0, lo - pad // 2), min(n, hi + pad // 2)
        if hi2 - lo2 >= 16:
            flats.append(flatness(took[lo2:hi2].sum(axis=1), upto))
    energy = float((took**2).sum())
    return {
        "spans_per_min": starts.size / (n / rate / 60),
        "touched_pct": 100.0 * touched.sum() / n,
        "removed_dbfs": 10 * np.log10(max(energy / took.size, 1e-30) / 32768.0**2),
        "peak_dbfs": 20 * np.log10(max(float(np.abs(took).max()), 1e-9) / 32768.0),
        "flatness": float(np.median(flats)) if flats else float("nan"),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", type=Path, default=Path("D:/tmp/bakeoff/real"))
    ap.add_argument("--out", type=Path, default=Path("D:/tmp/bakeoff/out"))
    ap.add_argument("--tools", nargs="+", default=["gc-s35", "gc-s50", "nd-s0", "wc-t3", "wc-t4"])
    a = ap.parse_args(argv)

    for src in sorted(a.src.glob("*.wav")):
        print(f"\n{src.name}")
        signal = sf.read(str(src), dtype="float64", always_2d=True)[0][:, 0]
        upto = occupied_bins(signal, sf.info(str(src)).samplerate)
        print(f"  band holding 99% of the energy: 0 to "
              f"{upto * sf.info(str(src)).samplerate / 2 / 1000:.1f} kHz")
        print(f"  {'tool':<14}{'spans/min':>11}{'touched':>9}{'removed dBFS':>14}"
              f"{'peak dBFS':>12}{'flatness':>10}")
        for tool in a.tools:
            got = a.out / tool / src.name
            if not got.exists():
                continue
            m = measure(src, got, upto)
            print(f"  {tool:<14}{m['spans_per_min']:>11,.0f}{m['touched_pct']:>8.2f}%"
                  f"{m['removed_dbfs']:>14.1f}{m['peak_dbfs']:>12.1f}{m['flatness']:>10.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
