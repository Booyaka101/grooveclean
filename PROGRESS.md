# Progress

Status as of 2026-09-10. Version 1.0.0 is complete and built, and has since had a review
pass over everything a user sees. This file records what shipped, what was measured, and what
was deliberately left out.

## Shipped

- `src/grooveclean/`: `io` (probe, blocked reads, odd-extension padding, exact integer
  quantisation), `detect` (resample, normalise, impulsiveness, clipping, CNN, hysteresis, span
  mapping), `repair` (batched LSAR order 64, cubic fallback, gap bridging), `report`, `cli`.
- `train/`: `_ia` (archive.org client, split hashing, harvest driver), `harvest_noise`,
  `harvest_clean`, `mix`, `metrics`, `train`, `fetch_test_assets`, `pick_clean_excerpt`,
  `make_credits`.
- 101 tests in the five groups the brief names, all passing offline with no GPU.
- `dist/grooveclean-1.0.0-py3-none-any.whl` (349 KB, weights included),
  `dist/grooveclean-1.0.0.tar.gz` (5.1 MB), `dist/grooveclean-win64.exe` (155 MB, CPU torch).
  All three rebuilt after the review pass. The wheel installs into an empty venv and cleans
  the bundled 78 with `max |out + removed - in| = 0`; the exe does the same with no Python on
  the path.
- README, CHANGELOG, CREDITS, LICENSE, `.github/workflows/ci.yml`.
- `docs/`: three generators and what they make. `make_figure.py` draws the README hero (one
  click at sample resolution, before and after spectrograms, and the waveform of the whole
  difference file). `make_demo.py` renders ten seconds of the bundled 78 to
  `docs/demo/*.mp3`, before, after and removed, so a visitor can hear it without installing
  anything. `make_screens.py` runs a command for real and draws its captured output, which is
  where the two terminal shots in the README come from.

## Measured

- Detector, on the held-out synthetic eval: F1 0.989, precision 0.996, recall 0.982, 0.6 false
  positives per minute of click-free material. 12000 steps, 426,667 harvested clicks over 357
  clean clips. Settings and figures in `src/grooveclean/weights/detector.json`.
- Golden: 2,181 clicks on the bundled 1917 transfer, 8.49% of its duration, pinned at 2%.
- Speed on a 25 minute 96 kHz 24-bit stereo side: 46s on an RTX 4090, 2m55s on an i9-14900K
  CPU, same 110,392 clicks either way. `out + removed == in` byte exact on that 863 MB file.
- Clone check over 158 functions of five statements or more: nothing at or over 50%, house
  rule is 60%.

## Known limits

The false positive figure is measured on the eval set's click-free half, which is the same
kind of material as the rest of it: mostly music sitting on a synthesised surface-noise bed,
because that is the condition the tool runs in. It is not a claim about every kind of audio.

`train/pick_clean_excerpt.py` measures the other case. Pointed at seventeen arbitrary netlabels
releases that a plain second-difference screen calls click-free, the detector left eleven of
them bit-for-bit untouched and removed something from the other six, the worst at a difference
peak of -8.6 dBFS.
The material where it removes the most is loud, distorted, high-frequency-dense electronic
music, where the second difference is a tenth of the peak amplitude everywhere and there is
nothing for a local impulse test to stand out against. Dropping `--sensitivity` to 0.1 cuts
those detections by six times and still finds 842 clicks on the 78 excerpt, so the knob works,
but it does not separate the two cleanly. A record with real transient damage on it is the job;
harsh noise is not, and the README says so.

## The user-facing review pass

Every option now carries help text; `--sensitivity`, `--device` and `batch --max-width-ms`
had none. Both commands carry a `short_help` so the group listing does not truncate
mid-sentence. Long error messages wrap into a paragraph on a terminal and stay on one line
down a pipe, the way the progress line already behaved. Pointing `--weights` at the wrong
file used to print six lines of PyTorch's `weights_only` essay; it now says the file is not a
checkpoint it can read.

One real bug came out of it. `clean -o side.xyz` guessed WAV for any extension it did not
recognise and wrote a WAV under a name nothing would open, and `-o side` with no extension
did the same. Unknown extensions are refused now, with the six containers listed, and
`test_an_output_name_with_no_known_format_is_refused` covers it.

## Deliberately not in 1.0.0

Ranked by how often they would actually be wanted.

- **Crossfade at the repair boundary.** Spans are substituted hard. A quarter-millisecond
  crossfade would hide the seam on the rare span where the AR fit ends at the wrong level.
  Left out because it would break the exact `out + removed == in` reporting of span residuals
  without a test that shows it helps.
- **Per-side summary of where the damage is.** The report lists spans; it does not say "the
  last four minutes of this side are ten times worse than the first". The report schema is
  pinned by the brief, so this wants a separate command rather than more keys.
- **Multi-file GPU batching.** `batch` processes files one at a time; a short file leaves the
  GPU mostly idle.
- **A `--threshold` escape hatch** exposing the raw (enter, leave) hysteresis pair instead of
  the single sensitivity knob. Useful for a second opinion on a hard side, but it is a second
  way to say the same thing and the sensitivity mapping is the supported one.
- **Stereo-correlation-aware detection.** A groove-wall tick usually lands on one wall a few
  samples before the other. The training mixer models that skew; the detector does not use it,
  because it scores each channel independently.
- **Anything in the brief's non-goals**: no hiss or broadband noise reduction, no wow and
  flutter, no de-hum, no EQ, no GUI, no plugin, no lossy input, no track splitting.

## Publishing

Nothing has been published. The wheel, sdist and exe are built and verified locally. PyPI
upload and the GitHub release are the owner's to run.
