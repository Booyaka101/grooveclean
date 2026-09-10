"""Fixtures: a matrix of small synthetic transfers, plus the two checked-in excerpts."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).resolve().parent / "data"
sys.path.insert(0, str(ROOT / "train"))

from grooveclean import detect  # noqa: E402

# name -> (sample rate, channels, subtype, container)
LAYOUTS = {
    "mono_44k_16": (44100, 1, "PCM_16", "wav"),
    "stereo_44k_24": (44100, 2, "PCM_24", "wav"),
    "stereo_96k_24": (96000, 2, "PCM_24", "flac"),
    "mono_192k_32": (192000, 1, "PCM_32", "wav"),
    "stereo_48k_float": (48000, 2, "FLOAT", "wav"),
}
SECONDS = 3.0
CLICKS_PER_S = 15.0


@dataclass(slots=True)
class Transfer:
    path: Path
    rate: int
    channels: int
    subtype: str
    clicks: int


def music(rate: int, seconds: float, channels: int, rng: np.random.Generator) -> np.ndarray:
    """Stand-in for a recording: a few harmonics, a slow swell, a little hiss. No impulses."""
    n = int(seconds * rate)
    t = np.arange(n) / rate
    out = np.empty((n, channels))
    for ch in range(channels):
        voice = sum(
            np.sin(2 * np.pi * f * (1.0 + 0.002 * ch) * t + rng.uniform(0.0, 2 * np.pi)) / k
            for k, f in enumerate((196.0, 294.0, 440.0, 587.0, 880.0), start=1)
        )
        voice *= 0.35 + 0.25 * np.sin(2 * np.pi * 0.7 * t + ch)
        out[:, ch] = voice + rng.normal(0.0, 0.004, n)
    return out * (0.5 / np.abs(out).max())


def one_click(rate: int, rng: np.random.Generator) -> np.ndarray:
    """A short decaying burst, the shape a groove defect leaves once the stylus recovers."""
    width = int(rng.integers(max(3, rate // 20000), max(6, rate // 2500)))
    t = np.arange(width)
    shape = np.sin(2 * np.pi * rng.uniform(0.18, 0.45) * t) * np.exp(-3.5 * t / width)
    return shape * rng.choice([-1.0, 1.0])


def sprinkle(
    data: np.ndarray, rate: int, rng: np.random.Generator, per_second: float
) -> tuple[np.ndarray, int]:
    """Add clicks well above the local level and return the count actually placed."""
    noisy = data.copy()
    n, channels = data.shape
    placed = 0
    for _ in range(int(round(per_second * n / rate))):
        click = one_click(rate, rng)
        at = int(rng.integers(rate // 100, n - rate // 100 - click.size))
        level = float(np.sqrt(np.mean(data[max(0, at - rate // 20) : at + rate // 20] ** 2)))
        gain = level * 10.0 ** (rng.uniform(10.0, 26.0) / 20.0)
        for ch in range(channels):
            if channels > 1 and rng.random() < 0.3:
                continue
            noisy[at : at + click.size, ch] += click * gain
        placed += 1
    peak = np.abs(noisy).max()
    return (noisy / peak * 0.97 if peak > 0.97 else noisy), placed


def write(path: Path, data: np.ndarray, rate: int, subtype: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), data, rate, subtype=subtype)


@pytest.fixture(scope="session")
def transfers(tmp_path_factory) -> dict[str, Transfer]:
    """One small file per layout, each with real clicks on it."""
    root = tmp_path_factory.mktemp("transfers")
    out = {}
    for index, (name, (rate, channels, subtype, container)) in enumerate(LAYOUTS.items()):
        rng = np.random.default_rng(1000 + index)
        clean = music(rate, SECONDS, channels, rng)
        noisy, placed = sprinkle(clean, rate, rng, CLICKS_PER_S)
        path = root / f"{name}.{container}"
        write(path, noisy, rate, subtype)
        out[name] = Transfer(path, rate, channels, subtype, placed)
    return out


@pytest.fixture(scope="session")
def clean_transfer(tmp_path_factory) -> Path:
    """Synthetic music with nothing impulsive in it at all."""
    rate = 44100
    rng = np.random.default_rng(77)
    path = tmp_path_factory.mktemp("clean") / "clean.wav"
    write(path, music(rate, 8.0, 2, rng), rate, "PCM_24")
    return path


@pytest.fixture(scope="session")
def detector() -> detect.Detector:
    return detect.Detector.load(None, "auto")


@pytest.fixture(scope="session")
def assets() -> dict:
    path = DATA / "ASSETS.json"
    if not path.exists():
        pytest.skip(f"{path} is missing; run python train/fetch_test_assets.py")
    return json.loads(path.read_text(encoding="utf-8"))


def read_exact(path: Path) -> np.ndarray:
    """Read as float64 in [-1, 1). Integer files go via int32, so sums stay bit exact."""
    info = sf.info(str(path))
    if info.subtype.startswith("PCM"):
        raw = sf.read(str(path), dtype="int32", always_2d=True)[0]
        return raw.astype(np.float64) / float(1 << 31)
    return sf.read(str(path), dtype="float64", always_2d=True)[0]
