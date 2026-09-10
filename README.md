# grooveclean

Offline declicker for vinyl and 78rpm transfers. It finds clicks with a small trained CNN,
fills each one by least-squares autoregressive interpolation, and writes three files: the
cleaned audio, the exact difference, and a JSON report of every click it touched.

![Spectrogram of a 1917 78rpm transfer before and after cleaning](https://raw.githubusercontent.com/Booyaka101/grooveclean/main/docs/before-after.png)

MIT licensed, no account, no upload, nothing phones home. Runs on a GPU if you have one and
falls back to the CPU if you do not.

## The difference file

`OUT.removed.wav` is the input minus the output, sample for sample. Play it and you hear only
what was taken away. If you hear a marimba note in there, the tool got it wrong, and you can
hear that in seconds instead of listening to a whole side twice trying to spot a hole.

The invariant is exact for integer formats, not approximate:

```
OUT.wav + OUT.removed.wav == IN.wav
```

That is what the first test group checks, on every bit depth and sample rate it supports.

## Install

```
pipx install grooveclean
```

or, if you want it in the current environment:

```
pip install grooveclean
```

On Windows there is a single-file `grooveclean-win64.exe` on the
[releases page](https://github.com/Booyaka101/grooveclean/releases). It needs no Python.

The PyPI package pulls in PyTorch, which is a large download. The CPU-only build is a lot
smaller if you have no GPU:

```
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install grooveclean
```

## Use

Clean one side:

```
grooveclean clean sideA.wav -o sideA.clean.wav
```

That writes `sideA.clean.wav`, `sideA.clean.removed.wav` and `sideA.clean.report.json`, and
prints a summary to stderr so you can pipe the audio around without it getting in the way.

Clean a folder:

```
grooveclean batch ./transfers -o ./cleaned
```

One file failing does not stop the run. The exit code is non-zero if any file was skipped.
`--skip-existing` leaves anything that already has a report in the output folder alone, which
is how you carry on after stopping a long batch. `--format flac` writes FLAC instead of WAV,
which is worth doing before you point it at a shelf of 96 kHz sides.

The output format follows the extension you ask for. `-o sideA.flac` writes FLAC, and the
difference file and report sit beside it. Sample rate, channel count and bit depth always
match the input, whatever the container.

### Options

| Option | Default | What it does |
| --- | --- | --- |
| `--sensitivity` | `0.5` | 0 finds only the obvious damage, 1 is aggressive. 0.5 is the trained operating point. |
| `--max-width-ms` | `20` | Longest span to interpolate. Anything wider is reported as `unrepaired` and left alone. |
| `--device` | `auto` | `cuda`, `cpu`, or `auto`. Asking for `cuda` without a GPU warns and uses the CPU. |
| `--dry-run` | off | Write only the report. Survey a stack of transfers without spending the disk. |
| `--weights` | bundled | Point at your own trained detector. |

Sensitivity is the knob to reach for first. If quiet passages come out with holes in them,
drop it to 0.3 and compare the difference files. If dense crackle is surviving, push it to
0.7. Everything else can stay where it is.

## The report

```json
{
  "input": "sideA.wav",
  "sample_rate": 96000,
  "channels": 2,
  "duration_s": 1504.31,
  "clicks": [
    {
      "channel": 0,
      "start_sample": 138204,
      "end_sample": 138219,
      "width_samples": 15,
      "confidence": 0.9931,
      "residual_rms": 0.00412617,
      "repair": "lsar"
    }
  ],
  "totals": { "count": 41882, "samples_repaired": 447120, "pct_of_duration": 0.31 }
}
```

`repair` is `lsar` for the normal case, `cubic` for a click too close to the start or end of
the file to fit a model around, and `unrepaired` for a span wider than `--max-width-ms`, which
is reported but left in the audio. `residual_rms` is the level of what was removed at that
click, so you can sort the report and go straight to the loudest thing the tool touched.

## What it does not do

Deliberately, so that what it does do can be checked:

- No hiss or broadband noise reduction. No spectral subtraction of any kind.
- No wow and flutter correction, no speed or pitch correction.
- No de-hum, no EQ, no filtering of any sort applied to the output.
- No GUI, no VST or AU plugin. It is a command line tool that processes files.
- No MP3, AAC, Vorbis or Opus input. Lossy encoding smears a click across the frame it sits
  in, and the codec's ringing is exactly the shape a declicker must not learn to chase.
- No cue sheets, no track splitting, no CD burning.

## How it works

The signal is resampled to 44.1 kHz and normalised for local level, then a dilated 1-D
convolutional network emits one click probability per sample. Every window in the analysis is
defined in milliseconds rather than samples, which is what makes a 44.1 kHz transfer and a 192
kHz transfer behave the same way.

Spans are taken by hysteresis on that probability, mapped back to the file's own sample rate,
and trimmed to the samples that are genuinely impulsive there. Clipped runs are excluded: a
square-topped peak is impulsive but it is not a click, and treating it as one puts holes in
loud passages.

Each span is then filled by least-squares AR interpolation of order 64. An AR model is fitted
to the 256 samples either side and the missing samples are chosen to minimise that model's
prediction error over every window touching the gap. Every span in a channel is assembled into
one batched tensor and solved together, so a side with forty thousand clicks costs one solve
per size bucket rather than forty thousand solves.

Files are streamed as overlapping blocks with a second of context on each side, so a two-hour
192 kHz transfer costs the same memory as a three-minute one. The boundary between what one
block writes and what the next writes is pushed clear of any repaired span, so no click is
ever written twice or cut in half.

### The detector was trained on real damage

Clicks are not synthesised. They are harvested from FLAC transfers in the Internet Archive's
78rpm collection: a 78 has almost no musical energy above 10 kHz, so impulses are located in
the band above that, and the click waveform itself is taken as the AR interpolation residual
over the full band. What the interpolator removes is the tick, and what it leaves is the
music. How large a residual counts is calibrated per transfer against the same interpolation
run over randomly chosen click-free spans.

Those real clicks are then added to click-free music from the Internet Archive's netlabels
collection, at 0.1 to 200 events per second and 3 to 30 dB over the local level, which makes
the training mask exact: it is the support of what was added. Candidate clean tracks are run
through an impulse detector of their own and rejected if they are already clicky. Percussive
material is deliberately kept, because the model has to see snare hits labelled as not a
click. The music is rolled off at a random corner between 4 and 16 kHz for most segments,
since a shellac transfer has no music in its top octave and a model trained only on full-band
audio reads that empty band as one long anomaly.

Ten percent of the source items on both sides are held out by hash of the identifier, so no
recording contributes to both training and evaluation. See `train/` for the whole pipeline.

## Compared to what

**[Airwindows DeCrackle](https://www.airwindows.com/decrackle/)** is free, MIT licensed, and
runs in real time as an AU, VST, CLAP or LV2 plugin. Prefer it when you are working inside a
DAW, when you want to hear the change while you move the controls, or when the crackle is
light. Chris Johnson says plainly that it removes the loudest crackles rather than all of
them, and for a lot of records that is the right trade.

Prefer grooveclean when the job is offline batch work on a stack of transfers, when the
crackle is dense enough that a real-time algorithm has to stay conservative, or when you want
a report and a difference file you can audit afterwards. It is slower than real time on a CPU
and there is no plugin. The two tools are not really competing.

**[GTK Wave Cleaner](https://github.com/audioquality/gwc)** by Jeff Welty is the prior art for
the repair method here. It is a GTK editor for exactly this job and it has been doing
least-squares autoregressive interpolation of click spans for two decades. The name LSAR comes
from that project. grooveclean's interpolator is an independent implementation of the same
published method, written from the Janssen and Vaseghi formulation and batched for the GPU;
no gwc code is used, and gwc is GPL-2.0-or-later while this is MIT. If you want a waveform
editor with a click-by-click undo, and you are on Linux, use gwc.

## Accuracy

Detection is scored on held-out synthetic mixes built from source recordings the training run
never saw. A click counts as found if the detected span overlaps it at all, because a tick two
samples short at one edge is still a caught tick.

The shipped weights score F1 0.989 on that held-out set, precision 0.996 and recall 0.982, at
0.6 false positives per minute of click-free music. That click-free half is the same kind of
material as the rest of the set, mostly music sitting on a synthesised surface-noise bed, since
that is the condition the tool actually runs in. The test suite refuses to pass below F1 0.95 or
above one false positive per minute, so those numbers are a floor rather than a claim.
The training settings that produced them are in
[`src/grooveclean/weights/detector.json`](src/grooveclean/weights/detector.json).

The other measurement worth having is what it does to music nobody asked it to touch. Pointed
at seventeen arbitrary netlabels releases that a plain impulse screen calls click-free, it left
eleven of them bit-for-bit untouched and took something out of the other six. The six are loud,
distorted, high-frequency-dense electronic tracks where the waveform is jagged everywhere and a
local impulse test has nothing to stand out against. Lowering `--sensitivity` cuts that back but
does not separate the two cleanly, so if you are cleaning something that is not a groove
transfer, listen to the difference file first.

Speed, on a 25 minute 96 kHz 24-bit stereo side:

```
$ grooveclean clean sideA.wav -o sideA.clean.wav
sideA.wav  25:00  96000 Hz  2ch
detected 110,392 clicks (2.80% of duration)
repaired in 46s on cuda
```

That is an RTX 4090. The same side takes 2m55s with `--device cpu` on an i9-14900K. Both runs
find the same 110,392 clicks: the device decides where the arithmetic happens, not what comes
out of it.

## Running the tests

```
pip install -e ".[dev]"
pytest
```

A hundred tests in five groups, matching the five things that can go wrong: the reconstruction
invariant, the clean-audio guard, detector F1 and false positive rate, a golden click count on
a bundled 1917 transfer, and the command line's behaviour on mono, stereo, 44.1 kHz, 96 kHz
and lossy input. They run offline and need no GPU.

## Training your own detector

```
python train/harvest_noise.py --items 600 --out corpus/noise
python train/harvest_clean.py --items 400 --out corpus/clean
python train/harvest_clean.py --items 400 --redistributable
python train/train.py --steps 12000
```

The harvesters talk to archive.org and take a while. Nothing else in the project needs the
network. Training builds the held-out evaluation file itself if it is not already there, then
calibrates the two hysteresis thresholds against it and refuses to exit zero if the result
misses either gate.

The second clean harvest asks archive.org for public domain and CC-BY items only. Those are
the ones the evaluation file can be built from, since that file is checked into the repo.

## Credits

Click waveforms and clean music come from the Internet Archive's
[78rpm](https://archive.org/details/78rpm) and
[netlabels](https://archive.org/details/netlabels) collections. Per-item provenance for
everything that went into the shipped model is in [`CREDITS.md`](CREDITS.md).

The bundled test excerpt is the Imperial Marimba Band's 1917 recording of Sousa's *The Stars
and Stripes Forever*, in the public domain in the United States.

## Licence

MIT. See [LICENSE](LICENSE).
