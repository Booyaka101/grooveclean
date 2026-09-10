# Changelog

## 1.1.0 - 2026-09-10

New detector weights and a much quieter default operating point. Nothing about the command
line, the file formats or the output layout changed, so a 1.0.1 script still runs.

- Retrained on a broader damage model. A quarter of the injected clicks are now synthesised
  damped resonances rather than ticks harvested from real transfers, and a fifth of all damage
  replaces the samples underneath it instead of adding to them. Against the head-to-head
  corpus that is worth 3.1 dB on resonant damage and 4.6 dB on destructive damage, taking
  detection F1 on those two families from 0.65 and 0.72 to 0.96.
- The threshold calibration now breaks ties on sample-level F1 rather than on how wide the
  hysteresis band is. Event F1 only asks whether a detected span touches a click, so it is
  flat across a quarter of the search grid and the tie-break is what actually picks the
  shipped thresholds. The old rule chose a very low leave threshold, which let spans run on
  through noisy 78 material; the worst real side in the bench went from 22.7% of its samples
  touched to 6.2%.
- Held out scores moved from F1 0.989 at 0.6 false positives per minute to F1 0.994 with none
  at all. On 120 seconds of undamaged music at the default sensitivity it now disturbs 76
  frames per minute where 1.0.1 disturbed 236.
- The cost is about 4 dB of headroom on the faintest ticks. At the default sensitivity 1.1
  finds harvested clicks down to roughly 7 dB over the local music level where 1.0.1 reached
  about 4 dB. Raise `--sensitivity` if you were relying on that.
- `bench/` gained two held-out damage families the mixer does not generate, twelve whole real
  78 sides, a speed profile of all three tools and a measurement of what each does to music
  that is already clean. The honest result is written up in `bench/README.md`: broadening the
  training damage model bought accuracy on the damage that was added and did not generalise
  past it.
- The golden click count on the bundled 1917 Sousa excerpt is now 1,184 rather than 2,181,
  and the figures and screenshots in `docs/` are regenerated from the new weights.

## 1.0.1 - 2026-09-10

Documentation only. The code is unchanged from 1.0.0.

- The before and after demo now uses a 1925 Banner side rather than the 1917 Sousa excerpt
  the golden test is pinned to. The Sousa side is dense continuous crackle, and grooveclean
  removes impulses while leaving broadband hiss, so before and after measured 2.4 dB apart
  in 4-16 kHz and sounded the same. On the new side 95 ticks stand more than 20 dB above the
  music and none survive, which drops the peak from -0.7 to -11.9 dBFS while the music below
  1 kHz moves 0.11 dB.
- `docs/make_demo.py` normalises the loudest of the three files to -1 dBFS and applies that
  one gain to all three, so `before == after + removed` still holds.
- `tests/data/demo78.flac` is the new excerpt, held out of training and scoring, cut and
  credited by `train/fetch_test_assets.py`. It is excluded from the sdist.

## 1.0.0 - 2026-09-10

First release.

- `grooveclean clean IN.wav -o OUT.wav` writes the cleaned audio, the exact difference file
  and a JSON report of every click.
- `grooveclean batch DIR -o OUTDIR` runs the same over a folder and keeps going past a file
  it cannot read.
- `--dry-run` on both commands writes the report only, for surveying a stack of transfers.
- `--skip-existing` on `batch` picks up where an interrupted run stopped.
- `--format` on `batch` chooses the output container. WAV, FLAC, AIFF, W64, CAF or RF64.
- On `clean` the container follows the `-o` extension. A name it cannot map to a format
  is refused rather than quietly written as a WAV.
- Detection by a dilated 1-D CNN trained on real clicks harvested from 78rpm transfers,
  mixed into click-free netlabels music.
- Repair by least-squares autoregressive interpolation of order 64, batched so a whole side
  costs one solve per span width, with cubic fallback at the file edges.
- WAV, FLAC, AIFF, W64, CAF and RF64 input at 8 to 32 bit and 44.1 to 192 kHz, mono or
  stereo. Lossy input is refused with an explanation rather than processed.
- Streams in overlapping blocks, so file length is not bounded by memory.
- CUDA when it is there, CPU when it is not, `--device` to force either.
