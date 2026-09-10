"""The awkward inputs: clipping, DC, damage at the very edges, and crackle too wide to fill."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from conftest import music, one_click, read_exact, write
from grooveclean import cli, detect, io
from grooveclean.repair import CONTEXT

RATE = 44100


def clean_at(rate: int, seconds: float, channels: int = 1, seed: int = 21) -> np.ndarray:
    return music(rate, seconds, channels, np.random.default_rng(seed))


def test_clipping_is_not_mistaken_for_clicks(detector, tmp_path):
    """A square-topped peak has a huge second difference and is not damage."""
    data = clean_at(RATE, 4.0) * 2.4
    clipped = np.clip(data, -0.98, 0.98)
    assert detect.clipped(clipped[:, 0]).sum() > RATE // 100

    source = tmp_path / "hot.wav"
    write(source, clipped, RATE, "PCM_24")
    out = tmp_path / "hot.out.wav"
    built = cli.clean_file(source, out, detector=detector)

    assert built["totals"]["count"] == 0, built["clicks"][:3]
    assert np.array_equal(read_exact(out), read_exact(source))


def test_a_dc_offset_does_not_trigger_anything(detector, tmp_path):
    source = tmp_path / "dc.wav"
    write(source, clean_at(RATE, 4.0) * 0.4 + 0.35, RATE, "PCM_24")
    out = tmp_path / "dc.out.wav"
    built = cli.clean_file(source, out, detector=detector)
    assert built["totals"]["count"] == 0


@pytest.mark.parametrize("where", ["start", "end"])
def test_damage_at_the_file_edge_is_filled_and_flagged(detector, tmp_path, where):
    """There is no room for an AR fit there, so it has to say cubic rather than pretend."""
    rng = np.random.default_rng(31)
    data = clean_at(RATE, 3.0)
    click = one_click(RATE, rng) * 0.6
    at = 40 if where == "start" else data.shape[0] - 40 - click.size
    data[at : at + click.size, 0] += click

    source = tmp_path / f"{where}.wav"
    write(source, data, RATE, "PCM_24")
    out = tmp_path / f"{where}.out.wav"
    built = cli.clean_file(source, out, detector=detector)

    near_edge = [
        entry
        for entry in built["clicks"]
        if entry["start_sample"] < CONTEXT or entry["end_sample"] > built_frames(built) - CONTEXT
    ]
    assert near_edge, f"nothing found near the {where} of the file"
    assert all(entry["repair"] == "cubic" for entry in near_edge)
    assert np.isfinite(read_exact(out)).all()


def built_frames(built: dict) -> int:
    return int(round(built["duration_s"] * built["sample_rate"]))


def test_a_span_wider_than_the_limit_is_reported_but_left_alone(transfers, detector, tmp_path):
    """A span past --max-width-ms is still reported, but the audio is handed back untouched."""
    transfer = transfers["stereo_44k_24"]
    out = tmp_path / "capped.wav"
    built = cli.clean_file(transfer.path, out, detector=detector, max_width_ms=0.2)

    limit = int(round(0.2e-3 * transfer.rate))
    wide = [entry for entry in built["clicks"] if entry["width_samples"] > limit]
    assert wide, "nothing was wider than a fifth of a millisecond"
    assert all(entry["repair"] == "unrepaired" for entry in wide)
    assert all(entry["residual_rms"] == 0.0 for entry in wide)
    assert built["totals"]["samples_repaired"] == sum(
        entry["width_samples"] for entry in built["clicks"] if entry["repair"] != "unrepaired"
    )

    original, cleaned = read_exact(transfer.path), read_exact(out)
    for entry in wide:
        span = slice(entry["start_sample"], entry["end_sample"])
        assert np.array_equal(cleaned[span, entry["channel"]], original[span, entry["channel"]])


def test_the_same_damage_is_found_at_44k_and_96k(detector, tmp_path):
    """Every window is defined in milliseconds, so the sample rate must not change the answer.

    The 44.1 kHz file is the 96 kHz one resampled, so it is the same damage rather than a
    second draw from the same generator. The clicks sit well clear of the music so the count
    floor below tests the resampling rather than where the default sensitivity happens to be.
    """
    rng = np.random.default_rng(33)
    data = clean_at(96000, 3.0, seed=33)
    for _ in range(30):
        click = one_click(96000, rng)
        at = int(rng.integers(9600, data.shape[0] - 9600))
        data[at : at + click.size, 0] += click * 0.6

    counts = {}
    for rate in (96000, 44100):
        x = torch.from_numpy(data[:, 0].astype(np.float32))[None, :]
        n_out = int(round(data.shape[0] * rate / 96000))
        resampled = detect.resample(x, n_out).numpy().T
        source = tmp_path / f"{rate}.wav"
        write(source, resampled, rate, "PCM_24")
        counts[rate] = cli.clean_file(
            source, tmp_path / f"{rate}.out.wav", detector=detector
        )["totals"]["count"]
    assert counts[44100] >= 20 and counts[96000] >= 20
    assert abs(counts[44100] - counts[96000]) <= 0.25 * max(counts.values()), counts


def test_running_it_twice_gives_the_same_report(transfers, detector, tmp_path):
    transfer = transfers["stereo_44k_24"]
    first = cli.clean_file(transfer.path, tmp_path / "a.wav", detector=detector)
    second = cli.clean_file(transfer.path, tmp_path / "b.wav", detector=detector)
    assert first["clicks"] == second["clicks"]


def test_cleaning_an_already_cleaned_file_finds_almost_nothing(transfers, detector, tmp_path):
    transfer = transfers["stereo_44k_24"]
    once = tmp_path / "once.wav"
    first = cli.clean_file(transfer.path, once, detector=detector)
    second = cli.clean_file(once, tmp_path / "twice.wav", detector=detector)
    assert first["totals"]["count"] > 10
    assert second["totals"]["count"] <= 0.15 * first["totals"]["count"], (
        first["totals"], second["totals"]
    )


def test_digital_silence_is_survivable(detector, tmp_path):
    source = tmp_path / "silence.wav"
    write(source, np.zeros((RATE * 2, 2)), RATE, "PCM_16")
    built = cli.clean_file(source, tmp_path / "silence.out.wav", detector=detector)
    assert built["totals"]["count"] == 0


def test_a_file_shorter_than_the_fitting_context(detector, tmp_path):
    source = tmp_path / "tiny.wav"
    write(source, clean_at(RATE, 0.004), RATE, "PCM_16")
    out = tmp_path / "tiny.out.wav"
    built = cli.clean_file(source, out, detector=detector)
    assert io.probe(out).frames == io.probe(source).frames
    assert built["duration_s"] == pytest.approx(0.004, abs=1e-3)


def test_normalisation_is_scale_invariant():
    """Level normalisation is what lets one threshold work on a quiet and a loud transfer."""
    x = torch.from_numpy(clean_at(RATE, 1.0)[:, 0].astype(np.float32))[None, :]
    loud = detect.normalize(x, RATE)
    quiet = detect.normalize(x * 1e-3, RATE)
    assert torch.abs(loud - quiet).max() < 1e-3


def test_block_padding_continues_the_slope(tmp_path):
    """A mirror pad turns a gradient corner at frame 0, and the impulse test fires on corners."""
    t = np.arange(RATE) / RATE
    source = tmp_path / "sine.wav"
    write(source, (0.5 * np.sin(2 * np.pi * 50 * t))[:, None], RATE, "PCM_24")
    info = io.probe(source)

    block = next(iter(io.read_blocks(info, info.frames, 128))).data[:, 0]
    inside = np.abs(np.diff(block[128 : 128 + info.frames], n=2)).max()
    assert np.abs(np.diff(block, n=2)).max() <= 1.5 * inside


def test_the_first_and_last_sample_are_not_reported_as_clicks(detector, tmp_path):
    """Padding the block is an implementation detail; it must not put a click in the report."""
    data = clean_at(RATE, 3.0, seed=44) * 0.6
    # Cut both ends mid-slope, which is where a mirror pad looks most like an impulse.
    steep = int(np.argmax(np.abs(np.diff(data[:, 0]))))
    data = data[steep : steep + RATE * 2]

    source = tmp_path / "cut.wav"
    write(source, data, RATE, "PCM_24")
    built = cli.clean_file(source, tmp_path / "cut.out.wav", detector=detector)
    edges = [c for c in built["clicks"] if c["start_sample"] < 8 or c["end_sample"] > len(data) - 8]
    assert edges == []
