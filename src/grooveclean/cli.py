"""Command line entry point, and the block pipeline that ties detection to repair.

The file is streamed as overlapping blocks so a two-hour 192 kHz transfer costs the same
memory as a three-minute one. Each block is detected and repaired with a second of context on
both sides, and the boundary between what one block writes and what the next writes is pushed
clear of any click, so no repaired span is ever written twice or cut in half.
"""

from __future__ import annotations

import shutil
import sys
import textwrap
import time
from collections.abc import Callable
from contextlib import ExitStack, suppress
from pathlib import Path
from typing import NoReturn

import click
import numpy as np
import torch

from . import __version__, detect, io, report
from .repair import CONTEXT, METHOD_NAMES, UNREPAIRED, repair

# A CUDA allocation failure is a RuntimeError, not a MemoryError, and reads the same to a user.
OUT_OF_MEMORY = (MemoryError, torch.cuda.OutOfMemoryError)

CORE_SECONDS = 61.0
OVERLAP_SECONDS = 1.0
DEFAULT_MAX_WIDTH_MS = 20.0


def sidecars(dst: Path) -> tuple[Path, Path]:
    stem = dst.with_suffix("")
    return (
        stem.with_name(stem.name + ".removed" + dst.suffix),
        stem.with_name(stem.name + ".report.json"),
    )


def _process_block(
    block: io.Block,
    info: io.Info,
    detector: detect.Detector,
    hi: float,
    lo: float,
    gate: float,
    max_width: int,
) -> tuple[np.ndarray, list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]]:
    signal = np.ascontiguousarray(block.data.T) / info.scale
    prob = detector.probabilities(torch.from_numpy(signal), info.samplerate).cpu().numpy()
    offset = block.core_start - block.pre

    y = block.data.copy()
    found = []
    for ch in range(info.channels):
        active = detect.active_mask(signal[ch], info.samplerate, gate)
        starts, ends, conf = detect.spans(prob[ch], active, info.samplerate, hi, lo)
        methods = np.full(starts.size, UNREPAIRED, dtype=np.int8)
        if starts.size:
            fits = (ends - starts) <= max_width
            # The brief's edge rule is about the file, not the block: only a click in the
            # real first or last CONTEXT samples lacks the audio an AR fit needs.
            at_edge = (starts + offset < CONTEXT) | (ends + offset > info.frames - CONTEXT)
            column, done = repair(
                block.data[:, ch],
                starts[fits],
                ends[fits],
                device=detector.device,
                force_cubic=at_edge[fits],
            )
            y[:, ch] = column
            methods[fits] = done
        found.append((starts + offset, ends + offset, conf, methods))
    return y, found


def _boundary(edge: int, found: list, limit: int) -> int:
    """Push a write boundary out of any repaired click that straddles it."""
    moved = True
    while moved:
        moved = False
        for starts, ends, _, methods in found:
            hit = (methods != UNREPAIRED) & (starts < edge) & (ends > edge)
            if hit.any():
                edge = int(ends[hit].max())
                moved = True
    return min(edge, limit)


def clean_file(
    src: str | Path,
    dst: str | Path,
    *,
    detector: detect.Detector,
    sensitivity: float = 0.5,
    max_width_ms: float = DEFAULT_MAX_WIDTH_MS,
    progress: Callable[[int, int], None] | None = None,
    report_only: bool = False,
) -> dict:
    """Write dst, dst.removed.<ext> and dst.report.json. Returns the report.

    ``report_only`` still runs the full repair, because the report's residual levels are
    measured on what the repair actually removed; it just writes no audio.
    """
    dst = Path(dst)
    info = io.probe(src)
    removed_path, report_path = sidecars(dst)
    source = Path(src).resolve()
    if source in {dst.resolve(), removed_path.resolve(), report_path.resolve()}:
        raise io.AudioError(f"{src}: one of the three outputs is the input file; choose another -o")
    dst.parent.mkdir(parents=True, exist_ok=True)
    io.format_for(dst, info)  # up front, so a dry run refuses what the real run would refuse

    hi, lo, gate = detect.thresholds(sensitivity, detector.calibration.hi, detector.calibration.lo)
    max_width = max(1, int(round(max_width_ms * 1e-3 * info.samplerate)))
    core = max(1, int(CORE_SECONDS * info.samplerate))
    overlap = max(CONTEXT + max_width + 1, int(OVERLAP_SECONDS * info.samplerate))

    clicks: list[report.Click] = []
    emitted = 0
    try:
        with ExitStack() as stack:
            out_fh = None if report_only else stack.enter_context(io.Writer(dst, info))
            rem_fh = None if report_only else stack.enter_context(io.Writer(removed_path, info))
            for block in io.read_blocks(info, core, overlap):
                y, found = _process_block(block, info, detector, hi, lo, gate, max_width)
                block_end = block.core_start - block.pre + block.data.shape[0]
                edge = block.core_start + block.core_len
                stop = _boundary(edge, found, min(info.frames, block_end))
                lo_i = emitted - block.core_start + block.pre
                hi_i = stop - block.core_start + block.pre
                original = block.data[lo_i:hi_i]
                cleaned, removed = io.split(original, y[lo_i:hi_i], info)
                if out_fh is not None and rem_fh is not None:
                    out_fh.write(cleaned)
                    rem_fh.write(removed)

                for ch, (starts, ends, conf, methods) in enumerate(found):
                    # By start, so every span belongs to exactly one block. A span can only
                    # cross `stop` if it was left unrepaired, and then it contributes no residual.
                    own = (starts >= emitted) & (starts < stop)
                    for i in np.flatnonzero(own):
                        span = removed[starts[i] - emitted : min(ends[i], stop) - emitted, ch]
                        clicks.append(
                            report.Click(
                                channel=ch,
                                start_sample=int(starts[i]),
                                end_sample=int(ends[i]),
                                width_samples=int(ends[i] - starts[i]),
                                confidence=float(conf[i]),
                                residual_rms=(
                                    float(np.sqrt(np.mean((span / info.scale) ** 2)))
                                    if span.size
                                    else 0.0
                                ),
                                repair=METHOD_NAMES[int(methods[i])],
                            )
                        )
                emitted = stop
                if progress is not None:
                    progress(emitted, info.frames)

        if emitted != info.frames:
            raise io.AudioError(
                f"{src}: wrote {emitted} of {info.frames} frames; the block seams did not line up"
            )
    except BaseException:
        # A half-written side and its difference file look exactly like a finished pair.
        # Whatever went wrong is the interesting error, so a failed tidy-up stays quiet.
        # A dry run opened neither, and they may be a previous real run's output.
        for path in () if report_only else (dst, removed_path):
            with suppress(OSError):
                path.unlink(missing_ok=True)
        raise

    built = report.build(
        input_path=str(src),
        sample_rate=info.samplerate,
        channels=info.channels,
        frames=info.frames,
        clicks=clicks,
    )
    report.write(built, report_path)
    return built


# --------------------------------------------------------------------------- presentation


def _clock(seconds: float) -> str:
    total = int(round(seconds))
    hours, rest = divmod(total, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def _elapsed(seconds: float) -> str:
    minutes, secs = divmod(int(round(seconds)), 60)
    return f"{minutes}m{secs:02d}s" if minutes else f"{secs}s"


def _describe(path: Path, info: io.Info) -> str:
    return f"{path.name}  {_clock(info.duration_s)}  {info.samplerate} Hz  {info.channels}ch"


def _summarise(built: dict, seconds: float, device: str, verb: str = "repaired") -> str:
    totals = built["totals"]
    return (
        f"detected {totals['count']:,} clicks ({totals['pct_of_duration']:.2f}% of duration)\n"
        f"{verb} in {_elapsed(seconds)} on {device}"
    )


def _progress(started: float) -> Callable[[int, int], None] | None:
    """One overwritten line on a terminal. Nothing at all when stderr is a pipe."""
    if not sys.stderr.isatty():
        return None

    def tick(done: int, total: int) -> None:
        click.echo(
            f"\r  {100.0 * done / total:5.1f}%  {_elapsed(time.perf_counter() - started)}   ",
            nl=False,
            err=True,
        )

    return tick


def _detector(device: str, weights: str | None) -> detect.Detector:
    resolved = detect.resolve_device(device)
    if device == "cuda" and resolved.type != "cuda":
        click.echo("cuda was requested but is not available here, using cpu", err=True)
    return detect.Detector.load(weights, resolved)


def _wrap(message: str, indent: str) -> str:
    """A paragraph on a terminal, one unbroken line down a pipe so grep still works."""
    if not sys.stderr.isatty():
        return message
    width = max(40, min(shutil.get_terminal_size((88, 24)).columns, 96) - 8)
    return textwrap.fill(message, width, subsequent_indent=indent)


def _fail(message: str) -> NoReturn:
    raise click.ClickException(_wrap(message, "       "))


# --------------------------------------------------------------------------- commands

DEVICE_CHOICE = click.Choice(["auto", "cuda", "cpu"], case_sensitive=False)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="grooveclean")
def main() -> None:
    """Offline declicker for vinyl and 78rpm transfers.

    Finds the ticks and pops, interpolates over them, and writes what it took out to a
    second file so you can listen to it and check nothing musical went with them.
    """


@main.command(short_help="Declick one file.")
@click.argument("source", type=click.Path(path_type=Path))
@click.option("-o", "--output", required=True, type=click.Path(path_type=Path), help="Output file.")
@click.option(
    "--sensitivity",
    default=0.5,
    show_default=True,
    type=click.FloatRange(0.0, 1.0),
    help="0 finds only the obvious damage, 1 is aggressive. 0.5 is the trained point.",
)
@click.option(
    "--max-width-ms",
    default=DEFAULT_MAX_WIDTH_MS,
    show_default=True,
    type=click.FloatRange(0.01, 1000.0),
    help="Longest span to interpolate. Anything wider is reported unrepaired.",
)
@click.option(
    "--device",
    default="auto",
    show_default=True,
    type=DEVICE_CHOICE,
    help="Where to run the detector. Auto takes the GPU when there is one.",
)
@click.option("--weights", type=click.Path(path_type=Path), help="Override the bundled detector.")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Write only the report. No audio is written, and the run costs no disk.",
)
def clean(
    source: Path,
    output: Path,
    sensitivity: float,
    max_width_ms: float,
    device: str,
    weights: Path | None,
    dry_run: bool,
) -> None:
    """Declick one file into OUTPUT, OUTPUT.removed.<ext> and OUTPUT.report.json."""
    try:
        info = io.probe(source)
    except io.AudioError as exc:
        _fail(str(exc))
    click.echo(_describe(source, info), err=True)
    try:
        detector = _detector(device, str(weights) if weights else None)
        started = time.perf_counter()
        built = clean_file(
            source,
            output,
            detector=detector,
            sensitivity=sensitivity,
            max_width_ms=max_width_ms,
            progress=_progress(started),
            report_only=dry_run,
        )
    except (io.AudioError, detect.DetectorError) as exc:
        _fail(str(exc))
    except OUT_OF_MEMORY:
        _fail("ran out of memory; try --device cpu, or split the file into shorter sides")
    except OSError as exc:
        _fail(f"{output}: could not be written ({exc})")
    if sys.stderr.isatty():
        click.echo("\r" + " " * 24 + "\r", nl=False, err=True)
    verb = "surveyed" if dry_run else "repaired"
    click.echo(
        _summarise(built, time.perf_counter() - started, detector.device.type, verb), err=True
    )


@main.command(short_help="Declick a folder of files.")
@click.argument("directory", type=click.Path(path_type=Path))
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    help="Where to write results. Defaults to a cleaned/ folder inside DIRECTORY.",
)
@click.option(
    "--sensitivity",
    default=0.5,
    show_default=True,
    type=click.FloatRange(0.0, 1.0),
    help="0 finds only the obvious damage, 1 is aggressive. 0.5 is the trained point.",
)
@click.option(
    "--max-width-ms",
    default=DEFAULT_MAX_WIDTH_MS,
    show_default=True,
    type=click.FloatRange(0.01, 1000.0),
    help="Longest span to interpolate. Anything wider is reported unrepaired.",
)
@click.option(
    "--device",
    default="auto",
    show_default=True,
    type=DEVICE_CHOICE,
    help="Where to run the detector. Auto takes the GPU when there is one.",
)
@click.option("--weights", type=click.Path(path_type=Path), help="Override the bundled detector.")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Write only the report. No audio is written, and the run costs no disk.",
)
@click.option(
    "--skip-existing",
    is_flag=True,
    help="Leave files that already have a report in OUTPUT_DIR. Resumes an interrupted run.",
)
@click.option(
    "--format",
    "extension",
    default="wav",
    show_default=True,
    type=click.Choice(io.OUTPUT_FORMATS, case_sensitive=False),
    help="Container for the cleaned files. FLAC roughly halves what a stack of sides costs.",
)
def batch(
    directory: Path,
    output_dir: Path | None,
    sensitivity: float,
    max_width_ms: float,
    device: str,
    weights: Path | None,
    dry_run: bool,
    skip_existing: bool,
    extension: str,
) -> None:
    """Declick every audio file in DIRECTORY. Files that fail do not stop the run."""
    try:
        sources = io.audio_files(directory)
    except io.AudioError as exc:
        _fail(str(exc))
    if not sources:
        _fail(f"{directory}: no audio files to clean (WAV, FLAC, AIFF, W64, CAF or RF64)")

    destination = Path(output_dir) if output_dir else directory / "cleaned"
    if destination.resolve() in {s.parent.resolve() for s in sources}:
        _fail(f"{destination}: would overwrite the input files, choose another -o")
    destination.mkdir(parents=True, exist_ok=True)

    try:
        detector = _detector(device, str(weights) if weights else None)
    except detect.DetectorError as exc:
        _fail(str(exc))

    failed = 0
    for index, source in enumerate(sources, start=1):
        target = destination / f"{source.stem}.{extension.lower()}"
        prefix = f"[{index}/{len(sources)}] {source.name}"
        if skip_existing and sidecars(target)[1].exists():
            click.echo(f"{prefix}: already done", err=True)
            continue
        try:
            started = time.perf_counter()
            built = clean_file(
                source,
                target,
                detector=detector,
                sensitivity=sensitivity,
                max_width_ms=max_width_ms,
                report_only=dry_run,
            )
        except (io.AudioError, detect.DetectorError, OSError, *OUT_OF_MEMORY) as exc:
            failed += 1
            click.echo(_wrap(f"{prefix}: skipped, {exc}", "  "), err=True)
            continue
        totals = built["totals"]
        click.echo(
            f"{prefix}: {totals['count']:,} clicks "
            f"({totals['pct_of_duration']:.2f}%) in {_elapsed(time.perf_counter() - started)}",
            err=True,
        )
    verb = "surveyed" if dry_run else "cleaned"
    click.echo(f"{len(sources) - failed} of {len(sources)} {verb} into {destination}", err=True)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
