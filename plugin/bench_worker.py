"""Measure the two-second job budget using real audio, without a DAW or GPU.

Run with the dedicated worker environment: python plugin/bench_worker.py transfer.flac
This measures three-second context windows, not full-file throughput or listening quality.
"""

from __future__ import annotations

import argparse
import time

import numpy as np
import soundfile as sf
import torch

from grooveclean.detect import Detector, resample
from grooveclean.plugin_worker import process_audio


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 20:
        parser.error("repeats must be in 1..20")
    with sf.SoundFile(args.input) as source:
        rate = source.samplerate
        audio = source.read(rate * 3, dtype="float32", always_2d=True)
    if len(audio) != rate * 3 or audio.shape[1] not in (1, 2):
        parser.error("input must contain at least three seconds of mono or stereo audio")
    torch.set_num_threads(2)
    detector = Detector.load(device="cpu")
    print("CPU worker, two threads, 3 s window per 2 s output job; excludes IPC/startup")
    print("rate,channels,median_ms,max_ms,within_2s_budget")
    for target in (44100, 48000, 96000, 192000):
        with torch.inference_mode():
            native = resample(torch.from_numpy(audio.T.copy()), target * 3).numpy().T.copy()
        process_audio(native, target, detector=detector)
        timings = []
        for _ in range(args.repeats):
            start = time.perf_counter()
            process_audio(native, target, detector=detector)
            timings.append(time.perf_counter() - start)
        print(f"{target},{audio.shape[1]},{np.median(timings) * 1000:.1f},"
              f"{max(timings) * 1000:.1f},{max(timings) < 2.0}")


if __name__ == "__main__":
    main()
