# Progress

Status as of 2026-09-10. Version 1.1.0 is complete and built. This file records what shipped,
what was measured, and what was deliberately left out.

## Shipped

- `src/grooveclean/`: `io` (probe, blocked reads, odd-extension padding, exact integer
  quantisation), `detect` (resample, normalise, impulsiveness, clipping, CNN, hysteresis, span
  mapping), `repair` (batched LSAR order 64, cubic fallback, gap bridging), `report`, `cli`.
- `train/`: `_ia` (archive.org client, split hashing, harvest driver), `harvest_noise`,
  `harvest_clean`, `mix`, `metrics`, `train`, `fetch_test_assets`, `pick_clean_excerpt`,
  `make_credits`.
- 102 tests in the five groups the brief names, all passing offline with no GPU.
- `dist/grooveclean-1.0.1-py3-none-any.whl` (349 KB, weights included),
  `dist/grooveclean-1.0.1.tar.gz` (5.1 MB), `dist/grooveclean-win64.exe` (155 MB, CPU torch).
  The wheel installs into an empty venv and cleans the bundled 78 with
  `max |out + removed - in| = 0`; the exe does the same with no Python on the path.
- README, CHANGELOG, CREDITS, LICENSE, `.github/workflows/ci.yml`.
- `docs/`: three generators and what they make. `make_figure.py` draws the README hero (one
  click at sample resolution, before and after spectrograms, and the waveform of the whole
  difference file). `make_demo.py` renders ten seconds of a worn 1925 side to
  `docs/demo/*.mp3`, before, after and removed, so a visitor can hear it without installing
  anything. That side is a second bundled excerpt, held out of training and scoring, chosen
  because its ticks are audible where the golden Sousa excerpt's dense crackle is subtle.
  `make_screens.py` runs a command for real and draws its captured output, which is where the
  two terminal shots in the README come from.

## Measured

- Detector, on the held-out synthetic eval: F1 0.994, precision 0.999, recall 0.990, no false
  positives at all in the click-free half. 12000 steps, 426,667 harvested clicks over 357 clean
  clips. Settings and figures in `src/grooveclean/weights/detector.json`.
- Golden: 1,184 clicks on the bundled 1917 transfer, 4.47% of its duration, pinned at 2%.
- Speed on a 25 minute 96 kHz 24-bit stereo side: 44s on an RTX 4090, 2m51s on an i9-14900K
  CPU. The two devices disagree about one click in 67,647 and about 75 samples in 288 million,
  which is float32 summing in a different order on a GPU. `out + removed == in` byte exact on
  that 863 MB file.
- Head to head against Wave Corrector PE 3.9 and Needledropper's Declicker on 46 files across
  seven damage families, plus twelve real 78 sides and a speed profile. Tables and method in
  `bench/README.md`. Broadening the training damage model bought 3 to 5 dB on the families it
  added and nothing on the family it did not, which is written up rather than buried.
- Clone check over 186 functions of six lines or more: worst pair 47%, house rule is 60%.

## Known limits

The false positive figure is measured on the eval set's click-free half, which is the same
kind of material as the rest of it: mostly music sitting on a synthesised surface-noise bed,
because that is the condition the tool runs in. It is not a claim about every kind of audio.

`grooveclean batch --dry-run` over the held-out clean corpus measures the other case. Pointed
at forty arbitrary netlabels releases that a plain second-difference screen calls click-free,
the detector left eighteen of them bit-for-bit untouched, touched under 0.01% of the file on
fourteen more, and took a measurable amount out of the last eight. The worst touches 0.15% of
its duration.
The material where it removes the most is loud, distorted, high-frequency-dense electronic
music, where the second difference is a tenth of the peak amplitude everywhere and there is
nothing for a local impulse test to stand out against. Dropping `--sensitivity` cuts those
detections back but does not separate the two cleanly. A record with real transient damage on
it is the job; harsh noise is not, and the README says so.

1.1 buys its quieter default with about 4 dB of headroom on the faintest ticks: at the default
sensitivity it finds harvested clicks down to roughly 7 dB over the local music level where
1.0.1 reached about 4 dB. On `bench`'s percussive set that costs 1.5 dB of recovered signal.
Both are in `bench/README.md` next to what the change bought.

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

## Published

Shipped 2026-09-10 from commit `888678b`.

- <https://github.com/Booyaka101/grooveclean>, public, MIT.
- <https://pypi.org/project/grooveclean/1.0.0/>, wheel and sdist.
- Release `v1.0.0` carries `grooveclean-win64.exe` (162,186,199 bytes), the wheel and the sdist.
- CI was green on all four legs of that exact commit before the tag: ubuntu 3.11, ubuntu 3.13,
  windows 3.12, and the wheel job. Verified through the commit's check-runs API.
- Verified after the fact: `pip install grooveclean` into an empty venv, cleaned the 78 excerpt,
  `max |out + removed - in| = 0`. Same run from the release exe with no Python on the path.
- The README's raw.githubusercontent image and the three demo MP3s all return 200 with
  `image/png` and `audio/mpeg`, so the links in the README play rather than download as text.

### 1.0.1

Shipped 2026-09-10 from commit `1109a82`, a documentation-only patch. Nothing under `src/`
changed, so the wheel's code is identical to 1.0.0.

Cut rather than left unreleased because PyPI renders `README.md` as the project page, and
that page still called the demo the 1917 Sousa transfer while the MP3s it links are served
from `main` and already played the 1925 side. The listing contradicted its own audio.

- <https://pypi.org/project/grooveclean/1.0.1/>, wheel and sdist.
- Release `v1.0.1` carries `grooveclean-win64.exe` (162,186,688 bytes), the wheel and the sdist.
- CI green on all four legs of that exact commit before the tag, verified through the commit's
  check-runs API. The rebase merge produced a new SHA on main, so CI was re-checked on it
  rather than trusting the branch's result.
- Verified after the fact: `pip install grooveclean` into an empty venv gave 1.0.1, cleaned the
  78 excerpt to the golden 2,181 clicks with `max |out + removed - in| = 0`. The release exe
  did the same with no Python on the path.
- The published sdist and wheel metadata both carry the new demo text and neither carries the
  old line.
