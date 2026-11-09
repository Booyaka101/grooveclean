"""Persistent CPU worker for the VST3 bridge: ``python -m grooveclean.plugin_worker``.

All integers and samples are little endian. After loading the detector, emit GCREADY1.
Requests are <4sIIIIff (GCRQ, 1, rate, channels, frames, sensitivity, width_ms), followed
by interleaved float32 audio. Responses are <4sIII (GCRS, 1, status, frames), followed
by interleaved float32 audio only on success. Status 1 always has zero frames.

An invalid header or truncated request gets one failure response and ends the stream:
there is no safe resynchronization marker inside arbitrary audio. A processing failure
after a complete payload does not end the stream. Clean EOF between requests is normal.
"""

from __future__ import annotations

import math
import sys
from contextlib import redirect_stdout
from typing import TYPE_CHECKING, BinaryIO

import numpy as np

if TYPE_CHECKING:
    from .detect import Detector

import struct

READY = b"GCREADY1"
REQUEST = struct.Struct("<4sIIIIff")
RESPONSE = struct.Struct("<4sIII")
VERSION = 1
DEFAULT_THREADS = 2
# The lower bound must accept 0.01 after its float32 wire round trip.
MIN_WIDTH_MS = float(np.float32(0.01))
MAX_WIDTH_MS = 20.0


def _validate_request(
    sample_rate: int, channels: int, frames: int, sensitivity: float, max_width_ms: float
) -> None:
    if (isinstance(sample_rate, (bool, np.bool_))
            or not isinstance(sample_rate, (int, np.integer))
            or not 8000 <= sample_rate <= 192000):
        raise ValueError("sample_rate must be an integer in 8000..192000")
    if channels not in (1, 2):
        raise ValueError("channels must be 1 or 2")
    if not 1 <= frames <= sample_rate * 5:
        raise ValueError("frame_count must be positive and at most five seconds")
    if not math.isfinite(sensitivity) or not 0 <= sensitivity <= 1:
        raise ValueError("sensitivity must be finite and in 0..1")
    if not math.isfinite(max_width_ms) or not MIN_WIDTH_MS <= max_width_ms <= MAX_WIDTH_MS:
        raise ValueError("max_width_ms must be finite and in 0.01..20")


def process_audio(
    audio: np.ndarray,
    sample_rate: int,
    sensitivity: float = 0.5,
    max_width_ms: float = MAX_WIDTH_MS,
    *,
    detector: Detector,
) -> np.ndarray:
    """Return float64 cleaned [frames, channels] audio without changing the input.

    Float32 and float64 inputs are accepted. Native float64 distinctions reach the
    detector's clipping checks and repair; conversion to float32 happens at the wire.
    Only complete safe events within the width limit are eligible for repair.
    """
    audio = np.asarray(audio)
    if audio.ndim != 2 or audio.dtype.kind != "f" or audio.dtype.itemsize not in (4, 8):
        raise ValueError("audio must be a float32 or float64 [frames, channels] array")
    frames, channels = audio.shape
    _validate_request(sample_rate, channels, frames, sensitivity, max_width_ms)
    if not np.isfinite(audio).all():
        raise ValueError("audio must contain only finite samples")

    import torch

    from .repair import repair

    signal = np.array(audio, dtype=np.float64, copy=True)
    cleaned = signal.copy()
    max_width = max(1, int(round(max_width_ms * 1e-3 * sample_rate)))
    with torch.inference_mode():
        events = detector.events(
            torch.from_numpy(np.ascontiguousarray(signal.T)), sample_rate, sensitivity
        )
        for ch, (starts, ends, _) in zip(range(channels), events, strict=True):
            fits = (ends - starts) <= max_width
            starts, ends = starts[fits], ends[fits]
            if not starts.size:
                continue
            column, _ = repair(signal[:, ch], starts, ends, device=torch.device("cpu"))
            # Copy only event samples, even if a repair implementation changes its context.
            for start, end in zip(starts, ends, strict=True):
                cleaned[start:end, ch] = column[start:end]
    if not np.isfinite(cleaned).all():
        raise ValueError("repair produced nonfinite samples")
    return cleaned


def _read_exact(stream: BinaryIO, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        chunk = stream.read(size - len(data))
        if not chunk:
            break
        data.extend(chunk)
    return bytes(data)


def _respond(output: BinaryIO, payload: bytes | None = None, frames: int = 0) -> None:
    output.write(RESPONSE.pack(b"GCRS", VERSION, int(payload is None), frames))
    if payload is not None:
        output.write(payload)
    output.flush()


def _load_detector() -> Detector:
    from .detect import Detector

    return Detector.load(device="cpu")


def serve(
    input: BinaryIO,
    output: BinaryIO,
    detector: Detector | None = None,
    *,
    threads: int = DEFAULT_THREADS,
) -> int:
    """Serve requests until EOF; return 1 for a startup or framing failure, else 0.

    Dependencies and weights load once, before readiness. Diagnostics, including
    accidental Python prints in model code, go to stderr, never the protocol stream.
    """
    try:
        with redirect_stdout(sys.stderr):
            if type(threads) is not int or not 1 <= threads <= 8:
                raise ValueError("threads must be an integer in 1..8")
            import torch

            torch.set_num_threads(threads)
            if detector is None:
                with torch.inference_mode():
                    detector = _load_detector()
    except Exception as exc:
        print(f"GrooveClean worker startup failed: {exc}", file=sys.stderr)
        return 1

    output.write(READY)
    output.flush()
    while True:
        header = _read_exact(input, REQUEST.size)
        if not header:
            return 0
        try:
            if len(header) != REQUEST.size:
                raise ValueError("truncated request header")
            magic, version, rate, channels, frames, sensitivity, width = REQUEST.unpack(header)
            if magic != b"GCRQ" or version != VERSION:
                raise ValueError("invalid request magic or version")
            _validate_request(rate, channels, frames, sensitivity, width)
            # Validate all dimensions before multiplication, reading or allocating payloads.
            payload_size = frames * channels * 4
            payload = _read_exact(input, payload_size)
            if len(payload) != payload_size:
                raise ValueError("truncated audio payload")
        except ValueError as exc:
            print(f"GrooveClean worker invalid request: {exc}", file=sys.stderr)
            _respond(output)
            return 1

        try:
            with redirect_stdout(sys.stderr):
                audio = np.frombuffer(payload, dtype="<f4").reshape(frames, channels)
                cleaned = process_audio(audio, rate, sensitivity, width, detector=detector)
                with np.errstate(over="ignore", invalid="ignore"):
                    wire_audio = cleaned.astype("<f4")
                if not np.isfinite(wire_audio).all():
                    raise ValueError("repair output is not representable as finite float32")
                response_payload = wire_audio.tobytes(order="C")
        except Exception as exc:
            print(f"GrooveClean worker processing failed: {exc}", file=sys.stderr)
            _respond(output)
            continue
        _respond(output, response_payload, frames)


def main() -> int:
    if sys.platform == "win32":
        import msvcrt
        import os

        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    try:
        return serve(sys.stdin.buffer, sys.stdout.buffer)
    except (OSError, EOFError) as exc:
        print(f"GrooveClean worker I/O failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
