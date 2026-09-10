"""Build the bake-off corpus: same audio for every declicker, with ground truth kept.

Segments come from the held-out test split, so no clean clip and no harvested click here
was seen during training. Two departures from the training mixer, both chosen to avoid
flattering grooveclean:

  - no lowpass. The training mixer rolls the music off between 4 and 16 kHz to imitate a
    shellac transfer. Wave Corrector and Needledropper's are vinyl tools, so the corpus is
    left full band, which is the condition grooveclean is least tuned for.
  - stereo. Real vinyl is, and both competitors have cross-channel logic that mono would
    switch off.

Writes noisy.wav (the input every tool gets), clean.wav (the truth) and mask.npy per item.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train"))

import mix  # noqa: E402

RATE = mix.RATE


def transient_density(path: Path, limit: int = 30 * 44100) -> float:
    """Onsets per second, used to pick the drum-heavy clips the AR detectors struggle on."""
    x, sr = sf.read(str(path), frames=limit, dtype="float64", always_2d=True)
    if x.shape[0] < sr:
        return 0.0
    mono = x.mean(axis=1)
    hop, win = 256, 1024
    frames = (mono.size - win) // hop
    if frames < 8:
        return 0.0
    spec = np.abs(
        np.fft.rfft(
            np.lib.stride_tricks.sliding_window_view(mono, win)[::hop][:frames]
            * np.hanning(win),
            axis=1,
        )
    )
    flux = np.maximum(np.diff(spec, axis=0), 0.0).sum(axis=1)
    if flux.size < 8 or flux.std() == 0.0:
        return 0.0
    peaks = flux > flux.mean() + 2.0 * flux.std()
    return float(peaks.sum()) / (frames * hop / sr)


def resonant_bank(rng: np.random.Generator, count: int = 600) -> list[np.ndarray]:
    """Damage waveforms nothing here was trained on: a cartridge ringing, not a harvested tick.

    Peak-normalised to 1.0 and shaped like the harvested bank so the mixer's dB-over-music
    gain means the same thing, but longer-tailed and synthetic.
    """
    out = []
    for _ in range(count):
        length = int(rng.integers(12, 121))
        t = np.arange(length)
        wave = np.sin(2 * np.pi * rng.uniform(300.0, 9000.0) / RATE * t
                      + rng.uniform(0.0, 2 * np.pi)) * np.exp(-t / (length / rng.uniform(2.0, 6.0)))
        out.append((wave / np.abs(wave).max()).astype(np.float32))
    return out


class Gouge(mix.Mixer):
    """Damaged samples are replaced rather than added to: the stylus lost the groove wall."""

    def _damage(self, noisy, mask, ch, lo, hi, piece):  # noqa: ANN001
        noisy[ch, lo:hi] = piece
        mask[ch, lo:hi] = True


def build(out: Path, noise: Path, clean: Path, seconds: float, seed: int,
          only: list[str] | None) -> None:
    corpus = mix.load_corpus(noise, clean, "test")
    print(f"test split: {len(corpus.clicks):,} clicks, {len(corpus.clean)} clean clips")

    scored = sorted(((transient_density(p), p) for p in corpus.clean), reverse=True)
    percussive = [p for _, p in scored[: max(8, len(scored) // 5)]]
    print(f"percussive pool: {len(percussive)} clips, "
          f"{scored[0][0]:.1f} down to {scored[len(percussive) - 1][0]:.1f} onsets/s")

    segment = int(seconds * RATE)
    # The lowpass is a 78 impersonation the competitors were never aimed at. Off for everyone.
    saved, mix.LOWPASS_PROBABILITY = mix.LOWPASS_PROBABILITY, 0.0

    # Longer damage spans, so the event rate is capped to keep the destroyed fraction of the
    # segment in the same range as the harvested sets rather than an order above it.
    unseen = mix.replace(corpus, clicks=resonant_bank(np.random.default_rng(seed)))
    unseen_rate = (0.1, 60.0)
    sets = [
        ("general", corpus, 10, mix.EVENTS_PER_S, mix.Mixer),
        ("percussive", mix.replace(corpus, clean=percussive), 6, mix.EVENTS_PER_S, mix.Mixer),
        ("control", corpus, 6, (0.0, 0.0), mix.Mixer),
        ("unseen-add", unseen, 6, unseen_rate, mix.Mixer),
        ("unseen-gouge", unseen, 6, unseen_rate, Gouge),
    ]
    if only:
        sets = [s for s in sets if s[0] in only]
    manifest = []
    try:
        for name, pool, count, rate, engine in sets:
            for i in range(count):
                mixer = engine(pool, seed + hash(name) % 9973 + i, segment=segment,
                               channels=2, events_per_s=rate)
                noisy, truth, mask = mixer.draw()
                stem = out / f"{name}-{i:02d}"
                stem.parent.mkdir(parents=True, exist_ok=True)
                sf.write(f"{stem}.noisy.wav", noisy.T, RATE, subtype="PCM_16")
                sf.write(f"{stem}.clean.wav", truth.T, RATE, subtype="PCM_16")
                np.save(f"{stem}.mask.npy", np.packbits(mask.ravel()))
                events = int(np.diff(np.concatenate(([0], mask.any(axis=0).astype(np.int8))))
                             .clip(min=0).sum())
                manifest.append({"name": stem.name, "set": name, "events": events,
                                 "click_samples": int(mask.sum()), "frames": segment})
                print(f"  {stem.name}: {events} events, {int(mask.sum()):,} click samples")
    finally:
        mix.LOWPASS_PROBABILITY = saved

    path = out / "manifest.json"
    if only and path.exists():
        keep = [i for i in json.loads(path.read_text(encoding="utf-8")) if i["set"] not in only]
        manifest = keep + manifest
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\n{len(manifest)} items -> {out}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=Path("D:/tmp/bakeoff/corpus"))
    ap.add_argument("--noise", type=Path, default=ROOT / "corpus/noise")
    ap.add_argument("--clean", type=Path, default=ROOT / "corpus/clean")
    ap.add_argument("--seconds", type=float, default=20.0)
    ap.add_argument("--seed", type=int, default=20260910)
    ap.add_argument("--only", nargs="*", help="Build only these sets.")
    a = ap.parse_args(argv)
    build(a.out, a.noise, a.clean, a.seconds, a.seed, a.only)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
