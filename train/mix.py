"""Build (noisy, clean, mask) training triples from the two harvested corpora.

A clean netlabels segment gets a synthesised surface-noise bed and a Poisson stream of real
harvested clicks laid on top. Because the clicks are added rather than found, the mask is
exact: it is the support of what was added, sample for sample.

Everything is randomised over the ranges a real transfer spans. Event rate 0.1 to 200 per
second, click peak 3 to 30 dB over the local music level, time-stretch, polarity, whether a
tick lands on one channel or both, and how far up the music itself is rolled off. Segments
are generated on demand during training; this module also writes the fixed held-out
evaluation set the test suite scores against.

    python train/mix.py --split test --out tests/data/detector_eval
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _ia  # noqa: E402
import harvest_clean  # noqa: E402
from grooveclean import detect  # noqa: E402

RATE = detect.ANALYSIS_RATE
SEGMENT = 2 * RATE

MUSIC_DBFS = (-30.0, -12.0)
BED_SNR_DB = (10.0, 45.0)
BED_PROBABILITY = 0.8
CLIP_PROBABILITY = 0.15
CLIP_HEADROOM_DB = (-3.0, 1.0)  # where the ceiling sits relative to the segment peak
LOWPASS_PROBABILITY = 0.6
LOWPASS_HZ = (4000.0, 16000.0)

EVENTS_PER_S = (0.1, 200.0)
CLICK_OVER_MUSIC_DB = (3.0, 30.0)
STRETCH = (0.7, 1.6)
BOTH_CHANNELS_PROBABILITY = 0.5
CHANNEL_RATIO = (0.3, 1.0)
CHANNEL_SKEW = 3  # samples of arrival difference between the two groove walls
CORRELATION = (0.2, 0.95)

QUIET_IMPULSES_PER_S = 0.5  # ceiling for a clip used as click-free music in the eval set
# The eval file is checked into an MIT repo, so the music inside it has to be one of these.
REDISTRIBUTABLE = ("/publicdomain/", "/licenses/by/")


class CorpusError(Exception):
    pass


@dataclass(slots=True)
class Corpus:
    clicks: list[np.ndarray]
    beds: np.ndarray
    clean: list[Path]

    def __post_init__(self) -> None:
        if not self.clicks or not self.clean:
            raise CorpusError(
                "corpus is empty: run train/harvest_noise.py and train/harvest_clean.py first"
            )


def load_corpus(noise_dir: Path, clean_dir: Path, split: str) -> Corpus:
    clicks: list[np.ndarray] = []
    beds: list[np.ndarray] = []
    for path in sorted(noise_dir.glob("*.npz")):
        if _ia.split_of(path.stem) != split:
            continue
        with np.load(path) as blob:
            offsets, flat = blob["offsets"], blob["clicks"]
            pairs = zip(offsets[:-1], offsets[1:], strict=True)
            clicks.extend(flat[a:b] for a, b in pairs if b > a)
            if blob["beds"].size:
                beds.append(blob["beds"])
    clean = [p for p in sorted(clean_dir.glob("*.flac")) if _ia.split_of(p.stem) == split]
    stacked = np.concatenate(beds) if beds else np.zeros((0, RATE // 4), np.float32)
    return Corpus(clicks=clicks, beds=stacked, clean=clean)


def quietest(corpus: Corpus, limit: float = QUIET_IMPULSES_PER_S) -> Corpus:
    """The corpus restricted to clips with next to nothing impulsive in them.

    The false positive budget is a claim about genuinely clean music. The harvest keeps
    anything under five impulses a second so the model sees percussion labelled as not-a-click,
    but a clip at four would put real ticks inside a segment the scorer calls click-free and
    count the detector's hits on them as errors.
    """
    keep = []
    for path in corpus.clean:
        data, rate = sf.read(str(path), dtype="float32", always_2d=True)
        worst = max(
            harvest_clean.impulse_rate(np.ascontiguousarray(data[:, ch]), rate)
            for ch in range(data.shape[1])
        )
        if worst <= limit:
            keep.append(path)
    if not keep:
        raise CorpusError(
            f"no clean clip is under {limit} impulses/s, so the false positive rate would be "
            "measured against music that already has ticks in it. Harvest more items."
        )
    return replace(corpus, clean=keep)


def _spectral_noise(template: np.ndarray, length: int, rng: np.random.Generator) -> np.ndarray:
    """Noise of arbitrary length with the template's magnitude spectrum and random phase."""
    magnitude = np.abs(np.fft.rfft(template.astype(np.float64)))
    bins = length // 2 + 1
    shaped = np.interp(
        np.linspace(0.0, 1.0, bins), np.linspace(0.0, 1.0, magnitude.size), magnitude
    )
    phase = rng.uniform(0.0, 2.0 * np.pi, bins)
    phase[0] = 0.0
    if length % 2 == 0:
        phase[-1] = 0.0
    out = np.fft.irfft(shaped * np.exp(1j * phase), n=length)
    return out / max(1e-12, float(np.sqrt(np.mean(out**2))))


def _lowpass(x: np.ndarray, corner_hz: float) -> np.ndarray:
    """Roll the music off the way a cutting lathe did, 12 dB per octave above the corner.

    The clean corpus is full-band modern digital audio; the transfers this runs on are not.
    Without it the model only ever sees music above 8 kHz in segments where that band is
    music, and reads a real 78's empty top octave as one long anomaly.
    """
    spec = np.fft.rfft(x, axis=-1)
    freqs = np.fft.rfftfreq(x.shape[-1], 1.0 / RATE)
    return np.fft.irfft(spec / (1.0 + (freqs / corner_hz) ** 4), n=x.shape[-1], axis=-1)


def _stretch(click: np.ndarray, factor: float) -> np.ndarray:
    n = max(2, int(round(click.size * factor)))
    if n == click.size:
        return click.astype(np.float64)
    return np.interp(
        np.linspace(0.0, click.size - 1.0, n), np.arange(click.size), click.astype(np.float64)
    )


def _local_level(x: np.ndarray, at: int, width: int = RATE // 20) -> float:
    lo, hi = max(0, at - width), min(x.size, at + width)
    window = x[lo:hi]
    if window.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(window.astype(np.float64) ** 2)))


class Mixer:
    """Draws random (noisy, clean, mask) triples. Every array is [channels, SEGMENT]."""

    def __init__(
        self,
        corpus: Corpus,
        seed: int,
        segment: int = SEGMENT,
        channels: int = 2,
        events_per_s: tuple[float, float] = EVENTS_PER_S,
    ):
        self.corpus = corpus
        self.rng = np.random.default_rng(seed)
        self.segment = segment
        self.channels = channels
        self.events_per_s = events_per_s

    def _music(self) -> np.ndarray:
        rng = self.rng
        for _ in range(8):
            path = self.corpus.clean[rng.integers(len(self.corpus.clean))]
            with sf.SoundFile(str(path)) as fh:
                if fh.frames <= self.segment:
                    continue
                fh.seek(int(rng.integers(fh.frames - self.segment)))
                block = fh.read(self.segment, dtype="float64", always_2d=True)
            if block.shape[0] < self.segment:
                continue
            take = [int(rng.integers(block.shape[1])) for _ in range(self.channels)]
            music = np.ascontiguousarray(block[:, take].T)
            level = float(np.sqrt(np.mean(music**2)))
            if level <= 1e-6:
                continue
            target = 10.0 ** (rng.uniform(*MUSIC_DBFS) / 20.0)
            return music * (target / level)
        raise CorpusError("no clean clip in the corpus is long enough for a segment")

    def _bed(self) -> np.ndarray:
        rng = self.rng
        if self.corpus.beds.shape[0] == 0 or rng.random() > BED_PROBABILITY:
            return np.zeros((self.channels, self.segment))
        template = self.corpus.beds[rng.integers(self.corpus.beds.shape[0])]
        parts = [_spectral_noise(template, self.segment, rng) for _ in range(2)]
        rho = rng.uniform(*CORRELATION)
        bed = np.stack(
            [parts[0]] + [rho * parts[0] + np.sqrt(1.0 - rho**2) * parts[1]] * (self.channels - 1)
        )
        return bed[: self.channels]

    def _place(self, noisy: np.ndarray, mask: np.ndarray, music: np.ndarray) -> None:
        rng = self.rng
        low, high = self.events_per_s
        if high <= 0.0:
            return
        rate = np.exp(rng.uniform(np.log(low), np.log(high)))
        for _ in range(int(rng.poisson(rate * self.segment / RATE))):
            click = self.corpus.clicks[rng.integers(len(self.corpus.clicks))]
            click = _stretch(click, rng.uniform(*STRETCH)) * rng.choice([-1.0, 1.0])
            at = int(rng.integers(self.segment))
            gain = 10.0 ** (rng.uniform(*CLICK_OVER_MUSIC_DB) / 20.0)

            lead = int(rng.integers(self.channels))
            ratios = np.zeros(self.channels)
            ratios[lead] = 1.0
            if rng.random() < BOTH_CHANNELS_PROBABILITY:
                ratios[ratios == 0.0] = rng.uniform(*CHANNEL_RATIO)

            for ch, ratio in enumerate(ratios):
                if ratio <= 0.0:
                    continue
                # The two groove walls do not present the same damage at the same instant.
                skew = 0 if ch == lead else int(rng.integers(-CHANNEL_SKEW, CHANNEL_SKEW + 1))
                lo, hi = max(0, at + skew), min(self.segment, at + skew + click.size)
                if hi <= lo:
                    continue
                amplitude = ratio * gain * _local_level(music[ch], lo)
                if amplitude <= 0.0:
                    continue
                piece = click[lo - at - skew : hi - at - skew] * amplitude
                self._damage(noisy, mask, ch, lo, hi, piece)

    def _damage(
        self,
        noisy: np.ndarray,
        mask: np.ndarray,
        ch: int,
        lo: int,
        hi: int,
        piece: np.ndarray,
    ) -> None:
        """Write one click into the segment. Its own method so a bench can swap the model."""
        noisy[ch, lo:hi] += piece
        mask[ch, lo:hi] |= piece != 0.0

    def draw(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        rng = self.rng
        music = self._music()
        if rng.random() < LOWPASS_PROBABILITY:
            music = _lowpass(music, rng.uniform(*LOWPASS_HZ))
        level = float(np.sqrt(np.mean(music**2)))
        bed = self._bed() * (level * 10.0 ** (-rng.uniform(*BED_SNR_DB) / 20.0))
        clean = music + bed
        if rng.random() < CLIP_PROBABILITY:
            ceiling = float(np.abs(clean).max()) * 10.0 ** (rng.uniform(*CLIP_HEADROOM_DB) / 20.0)
            clean = np.clip(clean, -ceiling, ceiling)

        noisy = clean.copy()
        mask = np.zeros_like(noisy, dtype=bool)
        self._place(noisy, mask, music)
        peak = float(np.abs(noisy).max())
        if peak > 1.0:
            noisy, clean = noisy / peak, clean / peak
        return noisy, clean, mask


def redistributable(corpus: Corpus, manifest: Path) -> Corpus:
    """The corpus restricted to clean clips whose source licence allows us to ship the mix.

    netlabels releases carry everything from CC0 to BY-NC-ND. Without a manifest there is
    nothing to check against, which is the case when someone trains on their own corpus.
    """
    if not manifest.exists():
        return corpus
    licences = {
        item["identifier"]: item.get("licenseurl") or ""
        for item in json.loads(manifest.read_text(encoding="utf-8"))["items"]
    }
    keep = [
        path
        for path in corpus.clean
        if any(tag in licences.get(path.stem, "") for tag in REDISTRIBUTABLE)
    ]
    if not keep:
        raise CorpusError(
            f"{manifest}: no clean clip is public domain or CC-BY, so no evaluation set can "
            "be checked in. Harvest more items."
        )
    return replace(corpus, clean=keep)


def write_eval(
    corpus: Corpus, seed: int, clicky: int, clean_only: int, out: Path, manifest: Path
) -> None:
    """One long mono FLAC plus per-segment masks, small enough to check into the repo.

    Both halves are built from the same restricted pool: the whole file is checked in, so all
    of it has to be redistributable, and a stray real tick in the music would be scored as a
    false positive on one side and as a missed click on the other.
    """
    shippable = quietest(redistributable(corpus, manifest))
    loud = Mixer(shippable, seed, channels=1)
    quiet = Mixer(shippable, seed + 1, channels=1, events_per_s=(0.0, 0.0))
    audio: list[np.ndarray] = []
    masks: list[np.ndarray] = []
    kinds: list[int] = []
    for index in range(clicky + clean_only):
        mixer = loud if index < clicky else quiet
        noisy, _, mask = mixer.draw()
        audio.append(noisy[0].astype(np.float32))
        masks.append(mask[0])
        kinds.append(1 if index < clicky else 0)

    lengths = np.array([a.size for a in audio], dtype=np.int64)
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out.with_suffix(".flac")), np.concatenate(audio), RATE, subtype="PCM_16")
    np.savez_compressed(
        out.with_suffix(".npz"),
        bounds=np.concatenate(([0], np.cumsum(lengths))).astype(np.int64),
        mask=np.packbits(np.concatenate(masks)),
        kind=np.array(kinds, dtype=np.int8),
        rate=np.int64(RATE),
    )
    print(
        f"{out.with_suffix('.flac')}: {len(audio)} segments, {int(lengths.sum()) / RATE:.0f} s, "
        f"{sum(int(m.sum()) for m in masks):,} click samples"
    )


def load_eval(stem: Path) -> tuple[list[np.ndarray], list[np.ndarray], np.ndarray, int]:
    """Read back what write_eval produced: (segments, per-segment masks, kinds, rate)."""
    audio, rate = sf.read(str(stem.with_suffix(".flac")), dtype="float32")
    with np.load(stem.with_suffix(".npz")) as blob:
        bounds, kinds = blob["bounds"], blob["kind"]
        flat = np.unpackbits(blob["mask"])[: int(bounds[-1])].astype(bool)
    pairs = list(zip(bounds[:-1], bounds[1:], strict=True))
    return [audio[a:b] for a, b in pairs], [flat[a:b] for a, b in pairs], kinds, int(rate)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--noise", type=Path, default=Path("corpus/noise"))
    ap.add_argument("--clean", type=Path, default=Path("corpus/clean"))
    ap.add_argument("--split", default="test", choices=["train", "test"])
    ap.add_argument("--clicky", type=int, default=60)
    ap.add_argument("--clean-only", type=int, default=100)
    ap.add_argument("--seed", type=int, default=1979)
    ap.add_argument("--out", type=Path, default=Path("tests/data/detector_eval"))
    args = ap.parse_args(argv)

    corpus = load_corpus(args.noise, args.clean, args.split)
    print(
        f"{args.split}: {len(corpus.clicks):,} clicks, {corpus.beds.shape[0]} beds, "
        f"{len(corpus.clean)} clean clips",
        flush=True,
    )
    write_eval(
        corpus, args.seed, args.clicky, args.clean_only, args.out,
        args.clean / "manifest.json",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
