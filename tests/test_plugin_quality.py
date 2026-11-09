"""Small boundary regressions, not a listening-quality or blind-evaluation claim."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from grooveclean import cli, detect, io
from grooveclean.plugin_worker import process_audio


@pytest.fixture(scope="module")
def cpu_detector():
    previous = torch.get_num_threads()
    torch.set_num_threads(2)
    yield detect.Detector.load(device="cpu")
    torch.set_num_threads(previous)


@pytest.mark.parametrize("rate", [44100, 48000, 96000, 192000])
def test_click_across_stream_segment_boundary_matches_offline_repair(rate, cpu_detector):
    frames = rate * 5
    time = np.arange(frames) / rate
    clean = (.05 * np.sin(2 * np.pi * 440 * time)).astype(np.float32)[:, None]
    audio = clean.copy()
    # Each five-sample impulse crosses a two-second output seam.
    shape = np.array([.5, -.4, .25, -.15, .08], dtype=np.float32)
    for seam in (2 * rate, 4 * rate):
        audio[seam - 2:seam + 3, 0] += shape

    info = io.Info("memory", rate, 1, frames, "FLOAT", "WAV", 0, 1)
    hi, lo, gate = detect.thresholds(.5, cpu_detector.calibration.hi, cpu_detector.calibration.lo)
    reference, _ = cli._process_block(
        io.Block(audio.astype(np.float64), 0, frames, 0), info,
        cpu_detector, hi, lo, gate, int(round(.02 * rate)),
    )
    result = np.empty_like(audio)
    context, core = rate // 2, rate * 2
    for start in range(0, frames, core):
        window = np.zeros((core + 2 * context, 1), dtype=np.float32)
        left, right = max(0, start - context), min(frames, start + core + context)
        at = left - (start - context)
        window[at:at + right - left] = audio[left:right]
        cleaned = process_audio(window, rate, detector=cpu_detector)
        count = min(core, frames - start)
        result[start:start + count] = cleaned[context:context + count]

    for seam in (2 * rate, 4 * rate):
        region = slice(seam - 16, seam + 16)
        input_error = np.sum((audio[region] - clean[region]) ** 2)
        output_error = np.sum((result[region] - clean[region]) ** 2)
        assert output_error < input_error * .1, "boundary click was not repaired"
        np.testing.assert_allclose(result[region], reference[region], atol=1e-5, rtol=0)
