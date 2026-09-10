"""Build the bake-off corpus: same audio for every declicker, with ground truth kept.

Segments come from the held-out test split, so no clean clip and no harvested click here
was seen during training. Two departures from the training mixer, both chosen to avoid
flattering grooveclean:

  - no lowpass. The training mixer rolls the music off between 4 and 16 kHz to imitate a
    shellac transfer. Wave Corrector and Needledropper's are vinyl tools, so the corpus is
    left full band, which is the condition grooveclean is least tuned for.
  - stereo. Real vinyl is, and both competitors have cross-channel logic that mono would
    switch off.

Seven sets, in three groups. `general`, `percussive` and `control` are the harvested bank
laid on top of the groove, which is what the detector was first trained on. `resonant` and
`gouge` are the synthesised and destructive damage the training mixer gained in 1.1, so they
measure that change rather than generalisation. `scratch` and `dropout` are held out of
training deliberately and are the only honest read on damage nobody anticipated: a scratch is
spread over tens of milliseconds where every trained family is one short event, and a dropout
is quieter than the music it lands in where every trained family is louder.

Writes noisy.wav (the input every tool gets), clean.wav (the truth) and mask.npy per item.
"""

from __future__ import annotations

import argparse
import json
import sys
import zlib
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train"))

import mix  # noqa: E402

RATE = mix.RATE
# Both held-out families span far more samples than a tick, so the event rate is capped to
# keep the damaged fraction of a segment in the same range as the harvested sets.
LONG_RATE = (0.1, 60.0)
HARVESTED = {"synthetic": 0.0, "destructive": 0.0}


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


class Scratch(mix.Mixer):
    """A scratch the stylus crosses: one shock, then a decaying train of repeats.

    Held out of training. Every family the detector is trained on is a single short event.
    """

    def _shape(self) -> np.ndarray:
        rng = self.rng
        repeats = int(rng.integers(3, 13))
        gap = int(rng.integers(20, 400))
        decay = rng.uniform(0.55, 0.9)
        out = np.zeros(gap * (repeats - 1) + 64, np.float64)
        for i in range(repeats):
            n = int(rng.integers(6, 40))
            hit = rng.standard_normal(n) * np.exp(-np.arange(n) / max(1.0, n / 3.0))
            out[i * gap : i * gap + n] += hit * decay**i
        return (out / np.abs(out).max()).astype(np.float32)


class Dropout(mix.Mixer):
    """The stylus mistracks and the groove goes quiet and hissy instead of loud.

    Held out of training. Every family the detector is trained on is louder than the music it
    lands on, so a detector keyed on excess energy has nothing here to fire at.
    """

    def _shape(self) -> np.ndarray:
        rng = self.rng
        n = int(rng.integers(22, 900))  # 0.5 to 20 ms
        edges = np.minimum(np.arange(n), np.arange(n)[::-1])
        wave = rng.standard_normal(n) * np.minimum(1.0, edges / max(1.0, n * 0.05))
        return (wave / max(1e-9, float(np.abs(wave).max()))).astype(np.float32)


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

    sets = [
        ("general", corpus, 10, mix.EVENTS_PER_S, mix.Mixer, HARVESTED),
        ("percussive", mix.replace(corpus, clean=percussive), 6, mix.EVENTS_PER_S,
         mix.Mixer, HARVESTED),
        ("control", corpus, 6, (0.0, 0.0), mix.Mixer, HARVESTED),
        ("resonant", corpus, 6, LONG_RATE, mix.Mixer, {"synthetic": 1.0, "destructive": 0.0}),
        ("gouge", corpus, 6, LONG_RATE, mix.Mixer, {"synthetic": 1.0, "destructive": 1.0}),
        ("scratch", corpus, 6, LONG_RATE, Scratch, {"destructive": 0.0}),
        ("dropout", corpus, 6, LONG_RATE, Dropout,
         {"destructive": 1.0, "gain_db": (-25.0, -3.0)}),
    ]
    if only:
        sets = [s for s in sets if s[0] in only]
    manifest = []
    try:
        for name, pool, count, rate, engine, kwargs in sets:
            for i in range(count):
                mixer = engine(pool, seed + zlib.crc32(name.encode()) % 9973 + i,
                               segment=segment, channels=2, events_per_s=rate, **kwargs)
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
