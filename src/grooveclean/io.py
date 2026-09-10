"""Audio I/O that preserves sample rate and bit depth, and refuses lossy input.

Integer files are carried through the whole pipeline as float64 holding *left-justified
int32 sample values* rather than [-1, 1) floats. That keeps the quantisation grid explicit,
which is what makes `out + removed == in` exact rather than approximate.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

# Subtypes that survive a decode/encode round trip without loss. Anything libsndfile can
# open that is not in here is either lossy or a compander, and is refused.
LOSSLESS_SUBTYPES = {
    "PCM_S8": 1 << 24,
    "PCM_U8": 1 << 24,
    "PCM_16": 1 << 16,
    "PCM_24": 1 << 8,
    "PCM_32": 1,
}
FLOAT_SUBTYPES = {"FLOAT", "DOUBLE"}

AUDIO_SUFFIXES = {".wav", ".wave", ".flac", ".aif", ".aiff", ".aifc", ".w64", ".rf64", ".caf"}

INT_SCALE = float(1 << 31)


class AudioError(Exception):
    """Anything that stops grooveclean from reading or writing a file."""


class LossyInputError(AudioError):
    pass


@dataclass(slots=True)
class Info:
    path: str
    samplerate: int
    channels: int
    frames: int
    subtype: str
    format: str
    step: float   # quantisation step in the pipeline's units
    scale: float  # divide pipeline units by this to get nominal [-1, 1)

    @property
    def duration_s(self) -> float:
        return self.frames / self.samplerate if self.samplerate else 0.0

    @property
    def is_int(self) -> bool:
        return self.subtype in LOSSLESS_SUBTYPES


def probe(path: str | Path) -> Info:
    path = Path(path)
    if not path.exists():
        raise AudioError(f"{path}: no such file")
    if path.is_dir():
        raise AudioError(f"{path}: is a directory, not an audio file")
    try:
        info = sf.info(str(path))
    except Exception as exc:  # libsndfile raises a bare RuntimeError for unknown formats
        raise AudioError(f"{path}: cannot read as audio ({exc})") from exc

    if info.subtype in LOSSLESS_SUBTYPES:
        step, scale = float(LOSSLESS_SUBTYPES[info.subtype]), INT_SCALE
    elif info.subtype in FLOAT_SUBTYPES:
        step, scale = 0.0, 1.0
    else:
        raise LossyInputError(
            f"{path}: {info.format}/{info.subtype} is lossy audio. grooveclean reads "
            "uncompressed PCM and FLAC only (WAV, FLAC, AIFF, W64, CAF, RF64, at 16, 24 or "
            "32-bit or float). A lossy codec smears each click across the frame it sits in, "
            "so a declicker cannot tell the click from the codec's own ringing."
        )
    if info.frames == 0:
        raise AudioError(f"{path}: file contains no audio frames")
    return Info(
        path=str(path),
        samplerate=info.samplerate,
        channels=info.channels,
        frames=info.frames,
        subtype=info.subtype,
        format=info.format,
        step=step,
        scale=scale,
    )


@contextmanager
def _libsndfile(path: str | Path, what: str) -> Iterator[None]:
    """libsndfile signals a vanished file, a full disk or a read-only folder as RuntimeError."""
    try:
        yield
    except (RuntimeError, OSError) as exc:
        raise AudioError(f"{path}: {what} ({exc})") from exc


def pad_odd(body: np.ndarray, pre: int, post: int) -> np.ndarray:
    """Extend past each end by continuing the slope, not by turning a corner.

    A plain mirror matches in value but not in gradient, and a gradient corner is exactly what
    the second-difference impulse test fires on, so every file reported a click on its own
    first and last sample. Clamped to the block's own range so the clipping test still sees
    the real peak.
    """
    n = body.shape[0]
    low, high = body.min(axis=0), body.max(axis=0)
    parts = [body]
    if pre > 0:
        mirror = body[np.clip(np.arange(pre, 0, -1), 0, n - 1)]
        parts.insert(0, np.clip(2.0 * body[0] - mirror, low, high))
    if post > 0:
        mirror = body[np.clip(n - 2 - np.arange(post), 0, n - 1)]
        parts.append(np.clip(2.0 * body[-1] - mirror, low, high))
    return np.concatenate(parts, axis=0)


def _read_at(fh: sf.SoundFile, start: int, count: int, info: Info) -> np.ndarray:
    """Read `count` frames from `start`, extending off the file's own edges."""
    n = info.frames
    lo, hi = max(0, start), min(n, start + count)
    dtype = "int32" if info.is_int else "float64"
    with _libsndfile(info.path, f"read failed at frame {lo}"):
        fh.seek(lo)
        body = fh.read(hi - lo, dtype=dtype, always_2d=True).astype(np.float64, copy=False)
    if body.shape[0] != hi - lo:
        raise AudioError(f"{info.path}: ends at frame {lo + body.shape[0]}, the header says {n}")
    pre, post = lo - start, (start + count) - hi
    if pre <= 0 and post <= 0:
        return body
    return pad_odd(body, pre, post)


@dataclass(slots=True)
class Block:
    data: np.ndarray  # [pre + core + post, channels], float64 in pipeline units
    core_start: int   # absolute frame index of the first emitted frame
    core_len: int
    pre: int          # context frames before core_start inside `data`


def read_blocks(info: Info, core_frames: int, overlap_frames: int) -> Iterator[Block]:
    """Stream the file as overlapping blocks so files larger than RAM still work."""
    core_frames = max(1, int(core_frames))
    overlap_frames = max(0, int(overlap_frames))
    with _libsndfile(info.path, "cannot be opened"):
        fh = sf.SoundFile(info.path)
    with fh:
        for start in range(0, info.frames, core_frames):
            core_len = min(core_frames, info.frames - start)
            data = _read_at(fh, start - overlap_frames, overlap_frames * 2 + core_len, info)
            yield Block(data=data, core_start=start, core_len=core_len, pre=overlap_frames)


class Writer:
    """Streaming writer that keeps the input's sample rate, channel count and bit depth."""

    def __init__(self, path: str | Path, info: Info, fmt: str | None = None):
        self.info = info
        self.path = Path(path)
        fmt = fmt or format_for(self.path, info)
        with _libsndfile(self.path, "cannot be written"):
            self._fh = sf.SoundFile(
                str(path),
                mode="w",
                samplerate=info.samplerate,
                channels=info.channels,
                subtype=info.subtype,
                format=fmt,
            )

    def write(self, data: np.ndarray) -> None:
        grid = quantize(data, self.info)
        if self.info.is_int:
            out = grid.astype(np.int32)
        else:
            out = grid.astype(np.float32 if self.info.subtype == "FLOAT" else np.float64)
        with _libsndfile(self.path, "could not be written to the end"):
            self._fh.write(out)

    def close(self) -> None:
        self._fh.close()

    def __enter__(self) -> Writer:
        return self

    def __exit__(self, *exc) -> None:
        self.close()


CONTAINERS = {
    ".wav": "WAV",
    ".wave": "WAV",
    ".flac": "FLAC",
    ".aif": "AIFF",
    ".aiff": "AIFF",
    ".aifc": "AIFF",
    ".w64": "W64",
    ".caf": "CAF",
    ".rf64": "RF64",
}
# One spelling each, for the `batch --format` choice. Anything above still works on `-o`.
OUTPUT_FORMATS = ("wav", "flac", "aiff", "w64", "caf", "rf64")


def format_for(path: Path, info: Info) -> str:
    """The libsndfile format for an output path, refusing a container that cannot hold it."""
    fmt = CONTAINERS.get(path.suffix.lower())
    if fmt is None:
        known = ", ".join("." + name for name in OUTPUT_FORMATS)
        raise AudioError(f"{path}: cannot tell the format from that name; use one of {known}")
    if info.subtype not in sf.available_subtypes(fmt):
        raise AudioError(f"{path}: {fmt} cannot hold {info.subtype} audio; write a .wav instead")
    return fmt


def quantize(data: np.ndarray, info: Info) -> np.ndarray:
    """Snap to the output format's grid so `input - output` is itself exactly storable."""
    if info.is_int:
        # The rails are on the grid too: INT_SCALE - 1 is not a value a 16- or 24-bit file
        # can hold, and libsndfile would truncate it back down a whole step on the way out.
        return np.clip(np.rint(data / info.step) * info.step, -INT_SCALE, INT_SCALE - info.step)
    if info.subtype == "FLOAT":
        return data.astype(np.float32).astype(np.float64)
    return data


def split(original: np.ndarray, repaired: np.ndarray, info: Info) -> tuple[np.ndarray, np.ndarray]:
    """Quantise the repair onto the file's own grid and take the difference on that grid.

    Both output files are written from these two arrays, so `out + removed == in` holds
    exactly for integer formats instead of to within a rounding error.
    """
    out = quantize(repaired, info)
    if info.is_int:
        # Keep the difference inside int32 as well as the output itself, or the removed file
        # would clip and stop adding back up.
        top = INT_SCALE - info.step
        lo = np.maximum(-INT_SCALE, original - top)
        hi = np.minimum(top, original + INT_SCALE)
        out = np.clip(out, lo, hi)
    return out, original - out


def audio_files(directory: str | Path) -> list[Path]:
    directory = Path(directory)
    if not directory.is_dir():
        raise AudioError(f"{directory}: no such directory")
    return sorted(
        p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_SUFFIXES
    )
