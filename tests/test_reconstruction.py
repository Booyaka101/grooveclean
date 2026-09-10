"""Group 1: out + removed == in, on every layout, and across the block seams."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from conftest import LAYOUTS, music, read_exact, sprinkle, write
from grooveclean import cli, io

TOLERANCE = 1e-6


def span_mask(built: dict, shape: tuple[int, int]) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    for entry in built["clicks"]:
        mask[entry["start_sample"] : entry["end_sample"], entry["channel"]] = True
    return mask


def check(source, out, built) -> np.ndarray:
    """The invariant, plus the stronger claim that nothing outside a reported span moved."""
    removed_path, report_path = cli.sidecars(out)
    assert out.exists() and removed_path.exists() and report_path.exists()

    original, cleaned, removed = (read_exact(p) for p in (source, out, removed_path))
    assert cleaned.shape == original.shape == removed.shape
    assert np.abs(cleaned + removed - original).max() <= TOLERANCE
    stray = (cleaned != original) & ~span_mask(built, original.shape)
    assert not stray.any(), f"{int(stray.sum())} samples changed outside any reported click"
    return removed


@pytest.mark.parametrize("name", sorted(LAYOUTS))
def test_output_plus_removed_is_the_input(transfers, detector, tmp_path, name):
    transfer = transfers[name]
    out = tmp_path / f"{name}.wav"
    built = cli.clean_file(transfer.path, out, detector=detector)

    check(transfer.path, out, built)
    assert built["sample_rate"] == transfer.rate
    assert built["channels"] == transfer.channels
    assert built["totals"]["count"] == len(built["clicks"])
    assert 0.0 <= built["totals"]["pct_of_duration"] <= 100.0


@pytest.mark.parametrize("core_seconds", [0.4, 1.0, 2.5])
def test_seams_hold_at_any_block_size(transfers, detector, tmp_path, monkeypatch, core_seconds):
    """Every span still belongs to exactly one block when the blocks are far smaller."""
    monkeypatch.setattr(cli, "CORE_SECONDS", core_seconds)
    monkeypatch.setattr(cli, "OVERLAP_SECONDS", 0.2)
    transfer = transfers["stereo_44k_24"]
    out = tmp_path / "seams.wav"
    built = cli.clean_file(transfer.path, out, detector=detector)

    check(transfer.path, out, built)
    starts = [(entry["channel"], entry["start_sample"]) for entry in built["clicks"]]
    assert len(starts) == len(set(starts)), "a click was reported by two blocks"


def test_a_file_longer_than_one_block(detector, tmp_path):
    """The shipped block size, on a file long enough to actually reach a seam."""
    rate, seconds = 44100, cli.CORE_SECONDS + 12.0
    rng = np.random.default_rng(4242)
    source = tmp_path / "long.wav"
    noisy, placed = sprinkle(music(rate, seconds, 1, rng), rate, rng, 8.0)
    write(source, noisy, rate, "PCM_16")

    out = tmp_path / "long.out.wav"
    built = cli.clean_file(source, out, detector=detector)
    check(source, out, built)
    assert built["duration_s"] == pytest.approx(seconds, abs=0.01)
    assert built["totals"]["count"] > placed // 2


@pytest.mark.parametrize("subtype", sorted(io.LOSSLESS_SUBTYPES))
@pytest.mark.parametrize("sign", [1, -1])
def test_split_stays_on_the_grid_against_the_rails(subtype, sign):
    """A repair that overshoots full scale still has to leave a difference the file can hold.

    24-bit audio cannot store INT_SCALE - 1, so clamping to it writes a value a whole step
    away and `out + removed == in` quietly stops being true at the loudest samples.
    """
    step = float(io.LOSSLESS_SUBTYPES[subtype])
    info = io.Info("x", 44100, 1, 3, subtype, "WAV", step, io.INT_SCALE)
    top = io.INT_SCALE - step
    original = np.array([[sign * top], [sign * top], [0.0]])
    repaired = np.array([[-sign * 4 * io.INT_SCALE], [sign * 4 * io.INT_SCALE], [0.0]])

    out, removed = io.split(original, repaired, info)
    for name, values in (("out", out), ("removed", removed)):
        assert np.all(values % step == 0), f"{name} left the grid"
        assert np.all(values >= -io.INT_SCALE) and np.all(values <= top), f"{name} out of range"
    assert np.array_equal(out + removed, original)


def test_full_scale_audio_with_clicks_on_it(detector, tmp_path):
    """The 25 minute real-transfer case: clicks in a passage already pinned to the rails."""
    rate = 96000
    rng = np.random.default_rng(808)
    noisy, _ = sprinkle(music(rate, 4.0, 2, rng), rate, rng, 30.0)
    source = tmp_path / "hot.wav"
    write(source, np.clip(noisy * 3.0, -1.0, 1.0), rate, "PCM_24")

    out = tmp_path / "hot.out.wav"
    built = cli.clean_file(source, out, detector=detector)
    original, cleaned, removed = (read_exact(p) for p in (source, out, cli.sidecars(out)[0]))
    assert np.array_equal(cleaned + removed, original)
    assert built["totals"]["count"] > 0


def test_a_read_that_comes_up_short_is_caught(tmp_path):
    """A short block would shorten the output silently and still pass the seam check."""
    path = tmp_path / "short.wav"
    write(path, np.zeros((100, 1)), 44100, "PCM_16")
    lying = replace(io.probe(path), frames=1000)

    with pytest.raises(io.AudioError, match="the header says"):
        list(io.read_blocks(lying, 1000, 0))
