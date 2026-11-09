"""Binary bridge coverage using small deterministic detectors and CPU repair."""

from __future__ import annotations

import io
import os
import struct
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

from grooveclean import plugin_worker as worker
from grooveclean import repair


class FakeDetector:
    def __init__(self, spans=(), *, noisy=False, fail=False):
        self.spans = spans
        self.noisy = noisy
        self.fail = fail
        self.calls = []

    def events(self, audio, rate, sensitivity):
        assert audio.device.type == "cpu"
        assert audio.dtype == torch.float64
        assert torch.is_inference_mode_enabled()
        self.calls.append((audio.clone(), rate, sensitivity))
        if self.noisy:
            print("detector diagnostic")
        if self.fail:
            raise RuntimeError("deliberate detector failure")
        starts = np.array([start for start, _ in self.spans], dtype=np.int64)
        ends = np.array([end for _, end in self.spans], dtype=np.int64)
        return [(starts, ends, np.ones(starts.size)) for _ in audio]


def request(audio=None, **changes):
    if audio is None:
        audio = np.zeros((32, 1), dtype=np.float32)
    fields = dict(magic=b"GCRQ", version=1, rate=48000, channels=audio.shape[1],
                  frames=audio.shape[0], sensitivity=.5, width=20.)
    fields.update(changes)
    return struct.pack("<4sIIIIff", *fields.values()) + audio.astype("<f4").tobytes()


def responses(data, channels):
    assert data[:8] == b"GCREADY1"
    result = []
    at = 8
    for count in channels:
        magic, version, status, frames = struct.unpack_from("<4sIII", data, at)
        assert (magic, version) == (b"GCRS", 1)
        at += 16
        size = frames * count * 4
        audio = np.frombuffer(data[at:at + size], dtype="<f4").reshape(frames, count)
        result.append((status, frames, audio))
        at += size
    assert at == len(data)
    return result


@pytest.mark.parametrize("rate", [8000, 44100, 48000, 96000, 192000])
@pytest.mark.parametrize("channels", [1, 2])
def test_no_events_is_exact_identity_at_native_rate(rate, channels):
    audio = np.random.default_rng(10).normal(0, .1, (1024, channels)).astype(np.float32)
    original = audio.copy()
    detector = FakeDetector()
    cleaned = worker.process_audio(audio, rate, .73, detector=detector)
    np.testing.assert_array_equal(audio, original)
    np.testing.assert_array_equal(cleaned, audio)
    assert cleaned.dtype == np.float64
    assert len(detector.calls) == 1
    seen, seen_rate, sensitivity = detector.calls[0]
    np.testing.assert_array_equal(seen.numpy(), audio.T)
    assert (seen_rate, sensitivity) == (rate, .73)


def test_float64_native_distinctions_reach_detection_and_repair(monkeypatch):
    audio = np.full((64, 1), .5, dtype=np.float64)
    audio[31:34, 0] -= np.arange(3) * 1e-9
    detector = FakeDetector([(31, 34)])

    def fake_repair(x, starts, ends, *, device):
        assert torch.is_inference_mode_enabled()
        assert device.type == "cpu"
        assert x.dtype == np.float64
        np.testing.assert_array_equal(x, audio[:, 0])
        y = x.copy()
        y[31:34] -= 1e-10
        return y, np.zeros(1, dtype=np.int8)

    monkeypatch.setattr(repair, "repair", fake_repair)
    cleaned = worker.process_audio(audio, 48000, detector=detector)
    np.testing.assert_array_equal(detector.calls[0][0].numpy(), audio.T)
    np.testing.assert_allclose(cleaned[31:34, 0], audio[31:34, 0] - 1e-10, atol=0, rtol=0)


def test_only_complete_events_within_width_are_written(monkeypatch):
    audio = np.random.default_rng(8).normal(0, .01, (400, 2))
    detector = FakeDetector([(10, 14), (50, 60), (100, 111)])
    calls = []

    def fake_repair(x, starts, ends, *, device):
        assert device.type == "cpu"
        calls.append((starts.copy(), ends.copy()))
        # Deliberately change context too: the worker must not copy it back.
        return np.zeros_like(x), np.zeros(starts.size, dtype=np.int8)

    monkeypatch.setattr(repair, "repair", fake_repair)
    cleaned = worker.process_audio(audio, 10000, max_width_ms=1, detector=detector)
    expected = audio.copy()
    expected[10:14] = 0
    expected[50:60] = 0
    np.testing.assert_array_equal(cleaned, expected)
    assert len(calls) == 2
    for starts, ends in calls:
        np.testing.assert_array_equal(starts, [10, 50])
        np.testing.assert_array_equal(ends, [14, 60])
    removed = audio - cleaned
    np.testing.assert_array_equal(cleaned + removed, audio)
    np.testing.assert_array_equal(removed[100:111], 0)


def test_real_cpu_repair_and_removed_relation():
    rate = 48000
    audio = (.1 * np.sin(np.arange(2048) * 2 * np.pi * 440 / rate))[:, None]
    audio[1000:1003] += .5
    cleaned = worker.process_audio(audio, rate, detector=FakeDetector([(1000, 1003)]))
    assert np.max(np.abs(cleaned[1000:1003] - audio[1000:1003])) > .1
    outside = np.ones(2048, dtype=bool)
    outside[1000:1003] = False
    np.testing.assert_array_equal(cleaned[outside], audio[outside])
    np.testing.assert_allclose(cleaned + (audio - cleaned), audio, atol=1e-16, rtol=0)


@pytest.mark.parametrize("audio,rate,sensitivity,width", [
    (np.zeros(10, dtype=np.float32), 48000, .5, 20),
    (np.zeros((10, 0), dtype=np.float32), 48000, .5, 20),
    (np.zeros((10, 3), dtype=np.float32), 48000, .5, 20),
    (np.zeros((0, 1), dtype=np.float32), 48000, .5, 20),
    (np.zeros((40001, 1), dtype=np.float32), 8000, .5, 20),
    (np.zeros((10, 1), dtype=np.int16), 48000, .5, 20),
    (np.zeros((10, 1), dtype=np.complex64), 48000, .5, 20),
    (np.zeros((10, 1), dtype=np.float32), 7999, .5, 20),
    (np.zeros((10, 1), dtype=np.float32), 192001, .5, 20),
    (np.zeros((10, 1), dtype=np.float32), 48000., .5, 20),
    (np.zeros((10, 1), dtype=np.float32), True, .5, 20),
    (np.zeros((10, 1), dtype=np.float32), 48000, -.01, 20),
    (np.zeros((10, 1), dtype=np.float32), 48000, 1.01, 20),
    (np.zeros((10, 1), dtype=np.float32), 48000, float("nan"), 20),
    (np.zeros((10, 1), dtype=np.float32), 48000, float("inf"), 20),
    (np.zeros((10, 1), dtype=np.float32), 48000, .5, .009),
    (np.zeros((10, 1), dtype=np.float32), 48000, .5, 20.01),
    (np.zeros((10, 1), dtype=np.float32), 48000, .5, float("nan")),
    (np.zeros((10, 1), dtype=np.float32), 48000, .5, float("inf")),
    (np.full((10, 1), np.nan), 48000, .5, 20),
    (np.full((10, 1), np.inf), 48000, .5, 20),
    (np.full((10, 1), -np.inf), 48000, .5, 20),
])
def test_process_validation_precedes_detection(audio, rate, sensitivity, width):
    detector = FakeDetector()
    with pytest.raises(ValueError):
        worker.process_audio(audio, rate, sensitivity, width, detector=detector)
    assert not detector.calls


@pytest.mark.parametrize("sensitivity,width", [(0., .01), (1., 20.)])
def test_wire_parameter_endpoints_are_accepted(sensitivity, width):
    output = io.BytesIO()
    assert worker.serve(io.BytesIO(request(sensitivity=sensitivity, width=width)), output,
                        FakeDetector()) == 0
    assert responses(output.getvalue(), [1])[0][:2] == (0, 32)


def test_five_second_limit_is_inclusive():
    audio = np.zeros((8000 * 5, 1), dtype=np.float32)
    cleaned = worker.process_audio(audio, 8000, detector=FakeDetector())
    np.testing.assert_array_equal(cleaned, audio)


def test_persistent_worker_payload_is_interleaved_and_loads_once(monkeypatch, capsys):
    detector = FakeDetector(noisy=True)
    loads = []

    def load():
        loads.append(True)
        print("loader diagnostic")
        return detector

    monkeypatch.setattr(worker, "_load_detector", load)
    first = np.array([[.1, -.7], [.2, -.8], [.3, -.9]], dtype=np.float32)
    second = np.array([[.6], [.4]], dtype=np.float32)
    output = io.BytesIO()
    assert worker.serve(io.BytesIO(request(first) + request(second, rate=96000)), output) == 0
    result = responses(output.getvalue(), [2, 1])
    for (status, frames, actual), expected in zip(result, [first, second], strict=True):
        assert (status, frames) == (0, len(expected))
        np.testing.assert_array_equal(actual, expected)
    assert len(loads) == 1
    assert len(detector.calls) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "loader diagnostic" in captured.err
    assert captured.err.count("detector diagnostic") == 2


def test_fragmented_stream_reads_are_reassembled():
    class Fragmented(io.BytesIO):
        def read(self, size=-1):
            return super().read(min(size, 3))

    output = io.BytesIO()
    assert worker.serve(Fragmented(request() + request()), output, FakeDetector()) == 0
    assert [row[:2] for row in responses(output.getvalue(), [1, 1])] == [(0, 32), (0, 32)]


@pytest.mark.parametrize("changes", [
    {"magic": b"NOPE"}, {"version": 0}, {"version": 2},
    {"rate": 7999}, {"rate": 192001}, {"rate": 0xffffffff},
    {"channels": 0}, {"channels": 3}, {"channels": 0xffffffff},
    {"frames": 0}, {"frames": 240001}, {"frames": 0xffffffff},
    {"sensitivity": -.01}, {"sensitivity": 1.01}, {"sensitivity": float("nan")},
    {"sensitivity": float("inf")}, {"width": .009}, {"width": 20.01},
    {"width": float("nan")}, {"width": float("inf")},
])
def test_bad_header_rejected_before_payload_read(changes, capsys):
    class HeaderOnly(io.BytesIO):
        def read(self, size=-1):
            assert self.tell() < 28, "invalid header reached payload allocation/read"
            return super().read(size)

    output = io.BytesIO()
    detector = FakeDetector()
    assert worker.serve(HeaderOnly(request(**changes)), output, detector) == 1
    assert responses(output.getvalue(), [1])[0][:2] == (1, 0)
    assert not detector.calls
    captured = capsys.readouterr()
    assert not captured.out
    assert "invalid request" in captured.err


@pytest.mark.parametrize("length", [1, 4, 27, 28, 29, 31, 28 + 127])
def test_truncated_header_or_payload_fails_without_partial_success(length, capsys):
    output = io.BytesIO()
    detector = FakeDetector()
    assert worker.serve(io.BytesIO(request()[:length]), output, detector) == 1
    assert responses(output.getvalue(), [1])[0][:2] == (1, 0)
    assert not detector.calls
    assert "truncated" in capsys.readouterr().err


def test_eof_between_requests_is_normal():
    output = io.BytesIO()
    assert worker.serve(io.BytesIO(), output, FakeDetector()) == 0
    assert output.getvalue() == b"GCREADY1"


@pytest.mark.parametrize("bad_value", [np.nan, np.inf, -np.inf])
def test_nonfinite_payload_errors_and_next_request_succeeds(bad_value, capsys):
    bad = np.full((16, 2), bad_value, dtype=np.float32)
    output = io.BytesIO()
    detector = FakeDetector()
    assert worker.serve(io.BytesIO(request(bad) + request()), output, detector) == 0
    assert [row[:2] for row in responses(output.getvalue(), [2, 1])] == [(1, 0), (0, 32)]
    assert len(detector.calls) == 1
    captured = capsys.readouterr()
    assert not captured.out
    assert "finite" in captured.err


def test_processing_exception_does_not_close_worker(capsys):
    class FailOnce(FakeDetector):
        def events(self, *args):
            self.fail = not self.calls
            return super().events(*args)

    output = io.BytesIO()
    assert worker.serve(io.BytesIO(request() + request()), output, FailOnce()) == 0
    assert [row[:2] for row in responses(output.getvalue(), [1, 1])] == [(1, 0), (0, 32)]
    assert "deliberate detector failure" in capsys.readouterr().err


@pytest.mark.parametrize("value", [np.nan, np.inf, float(np.finfo(np.float32).max) * 2])
def test_bad_repair_output_returns_failure_not_audio(monkeypatch, value, capsys):
    def bad_repair(x, starts, ends, **kwargs):
        result = x.copy()
        result[starts[0]:ends[0]] = value
        return result, np.zeros(starts.size, dtype=np.int8)

    monkeypatch.setattr(repair, "repair", bad_repair)
    output = io.BytesIO()
    assert worker.serve(io.BytesIO(request()), output, FakeDetector([(10, 12)])) == 0
    assert responses(output.getvalue(), [1])[0][:2] == (1, 0)
    assert "processing failed" in capsys.readouterr().err


def test_startup_failure_never_claims_readiness(monkeypatch, capsys):
    def fail():
        raise RuntimeError("weights unavailable")

    monkeypatch.setattr(worker, "_load_detector", fail)
    output = io.BytesIO()
    assert worker.serve(io.BytesIO(), output) == 1
    assert not output.getvalue()
    assert "weights unavailable" in capsys.readouterr().err


@pytest.mark.parametrize("threads", [0, 9, True, 2.5])
def test_thread_count_is_bounded(threads, capsys):
    output = io.BytesIO()
    assert worker.serve(io.BytesIO(), output, FakeDetector(), threads=threads) == 1
    assert not output.getvalue()
    assert "threads" in capsys.readouterr().err


def test_default_torch_threads_are_two(monkeypatch):
    calls = []
    monkeypatch.setattr(torch, "set_num_threads", calls.append)
    assert worker.serve(io.BytesIO(), io.BytesIO(), FakeDetector()) == 0
    assert calls == [2]


def test_module_entrypoint_with_bundled_cpu_model():
    rate = 48000
    clean = (.05 * np.sin(np.arange(rate) * 2 * np.pi * 440 / rate)).astype(np.float32)
    audio = np.stack([clean, clean], axis=1)
    audio[rate // 2, 1] += .65
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    completed = subprocess.run(
        [sys.executable, "-m", "grooveclean.plugin_worker"],
        input=request(audio) + request(np.zeros((32, 1), dtype=np.float32)),
        capture_output=True, env=env, timeout=60, check=False,
    )
    assert completed.returncode == 0, completed.stderr.decode(errors="replace")
    first, second = responses(completed.stdout, [2, 1])
    assert first[:2] == (0, rate)
    assert second[:2] == (0, 32)
    np.testing.assert_array_equal(first[2][:, 0], audio[:, 0])
    assert abs(float(first[2][rate // 2, 1]) - float(audio[rate // 2, 1])) > .3
    outside = np.abs(np.arange(rate) - rate // 2) > rate // 50
    np.testing.assert_array_equal(first[2][outside], audio[outside])
    assert not completed.stderr
