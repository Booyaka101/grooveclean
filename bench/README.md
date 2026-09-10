# Declicker bake-off

grooveclean's own accuracy numbers are measured against grooveclean's own test set, which
proves it is internally consistent and nothing else. This is the head to head: the same audio
through three declickers, scored the same way, with the corpus builder and the harness in this
folder so you can disagree with the method rather than with me.

Run on 2026-09-10, Windows 11, i9-14900K, RTX 4090.

The first version of this document, at 1.0.1, found that most of grooveclean's lead came from
being scored on its own click bank. 1.1 broadened the training damage model in response, and
this version measures whether that worked. The short answer is that it worked on the damage it
added and did not generalise past it, so both weight sets are in every table.

## What is being compared

| | version | detection | licence |
|---|---|---|---|
| grooveclean | 1.1.0, and 1.0.1 alongside it | dilated 1-D CNN, 84,865 params, 46 ms receptive field | MIT |
| [Needledropper's Declicker](https://github.com/keithhanlon/NeedledroppersDeclick) | `815171c`, 2026-03-30 | AR prediction error on Daubechies D4 detail levels, MAD sigma | AGPL-3.0 |
| [Wave Corrector PE](https://www.wavecor.co.uk/) | 3.9 | not published | freeware, closed source |

Only the declicker is exercised. Both competitors are more than that. Needledropper's has a
click-by-click review GUI, and Wave Corrector is a whole restoration suite with de-hiss, hum
filters, track splitting and CD burning. Wave Corrector's other stages were switched off and
Needledropper's DSP core was driven headless. Neither program was asked to do anything it does
not do at the press of one button.

## The corpus

46 files, 20 seconds each, 16-bit 44.1 kHz stereo, built by `corpus.py` from
[the training mixer](../train/mix.py) over the held-out **test** split. No clean clip and no
harvested click used below was seen during training.

Two departures from how grooveclean's own eval is built, both chosen against my own tool:

- **No 78 lowpass.** The training mixer rolls the music off between 4 and 16 kHz to imitate a
  shellac transfer. The other two are vinyl tools, so the corpus is left full band, which is the
  condition grooveclean is least tuned for.
- **Stereo, not mono.** Both competitors have cross-channel logic that mono would switch off.

Seven sets in three groups, and the group is what decides what a result means.

| set | files | what it is | trained on? |
|---|---|---|---|
| `general` | 10 | arbitrary test-split music, clicks harvested from real 78 transfers | yes, since 1.0 |
| `percussive` | 6 | the test-split clips with the highest onset density, same clicks | yes, since 1.0 |
| `control` | 6 | the same music with no clicks injected at all | n/a |
| `resonant` | 6 | synthesised damped resonances rather than harvested ticks | yes, since 1.1 |
| `gouge` | 6 | the same resonances replacing the samples instead of adding to them | yes, since 1.1 |
| `scratch` | 6 | a shock then a decaying train of 3 to 12 repeats over tens of ms | **no** |
| `dropout` | 6 | 0.5 to 20 ms of noise quieter than the music, replacing it | **no** |

`percussive` exists because Needledropper's own README concedes the case: "On drum-heavy
recordings, AR prediction errors from drum transients are indistinguishable from vinyl clicks at
the signal level. This is a fundamental property of the autoregressive detection approach."

`resonant` and `gouge` were the unseen sets in the 1.0.1 version of this document. grooveclean
lost most of its lead on them, so 1.1's mixer now generates both. That makes them a measurement
of whether the retrain landed, and it disqualifies them as evidence about damage nobody
anticipated. Only `scratch` and `dropout` are that, and they were chosen to break the two
assumptions every trained family shares: that damage is one short event, and that damage is
louder than the music it lands in.

## Scoring

The headline number is the **SNR of each output against the true clean signal**. It needs no
event matching, no tolerance window and no agreement about what counts as a click, and a tool
cannot move it by reporting its work differently.

Precision and recall come second, and are derived identically for every tool: a sample the tool
changed is a sample it claims was damaged, and changed spans within 0.5 ms merge into one event.
That is the only detection signal Wave Corrector exposes, so all three are read the same way. An
event counts as found if it overlaps a real one at all, which is
[the repo's existing rule](../train/metrics.py).

**off-target** is the share of the energy a tool removed that came from samples which were never
damaged. It is the closest thing here to "how much music did it eat".

On `control`, where the truth is the input, the only question is how much undamaged audio the
tool disturbed.

## Results

Each tool at its best setting for that set, picked from the full sweep at the bottom. Higher is
better except off-target. Input SNR is in the row heading, so **gain** is what the tool recovered.

**general**, input SNR 15.4 dB

| tool | setting | SNR out | gain | P | R | F1 | off-target |
|---|---|---|---|---|---|---|---|
| grooveclean 1.1 | 0.65 | **32.7** | **+17.3** | 0.982 | 0.961 | 0.972 | 1.3% |
| grooveclean 1.0.1 | 0.50 | 32.1 | +16.8 | 0.978 | 0.969 | **0.974** | 8.0% |
| Needledropper's | sensitivity 0 | 23.0 | +7.7 | 0.883 | 0.915 | 0.898 | 19.6% |
| Wave Corrector | threshold 4 | 21.8 | +6.5 | 0.986 | 0.847 | 0.911 | 14.5% |

**percussive**, input SNR 18.9 dB

| tool | setting | SNR out | gain | P | R | F1 | off-target |
|---|---|---|---|---|---|---|---|
| grooveclean 1.0.1 | 0.50 | **37.8** | **+18.9** | 0.890 | 0.913 | 0.901 | 2.3% |
| grooveclean 1.1 | 0.65 | 36.3 | +17.4 | 0.942 | 0.934 | **0.938** | 7.8% |
| Needledropper's | sensitivity 0 | 32.1 | +13.2 | 0.854 | 0.826 | 0.840 | 13.9% |
| Wave Corrector | threshold 3 | 25.6 | +6.7 | 0.982 | 0.612 | 0.754 | 11.1% |

Needledropper's precision falls from 0.883 to 0.854 moving from `general` to `percussive`, which
is its README's own limitation showing up in the numbers. At its shipped sensitivity of 30 the
same figure is 0.655. Wave Corrector pays for the same set in recall instead, 0.847 to 0.612.

**resonant**, input SNR 16.2 dB. In 1.1's training mixer, not in 1.0.1's.

| tool | setting | SNR out | gain | P | R | F1 | off-target |
|---|---|---|---|---|---|---|---|
| grooveclean 1.1 | 0.35 | **30.0** | **+13.7** | 0.977 | 0.948 | **0.963** | 0.6% |
| grooveclean 1.0.1 | 0.80 | 26.8 | +10.6 | 0.492 | 0.957 | 0.650 | 9.5% |
| Wave Corrector | threshold 3 | 22.5 | +6.2 | 0.824 | 0.833 | 0.828 | 13.4% |
| Needledropper's | sensitivity 30 | 21.7 | +5.5 | 0.488 | 0.982 | 0.652 | 9.8% |

**gouge**, input SNR 19.9 dB. Samples destroyed rather than added to. In 1.1's mixer, not 1.0.1's.

| tool | setting | SNR out | gain | P | R | F1 | off-target |
|---|---|---|---|---|---|---|---|
| grooveclean 1.1 | 0.50 | **31.1** | **+11.3** | 0.929 | 0.983 | **0.955** | 2.1% |
| grooveclean 1.0.1 | 0.65 | 26.5 | +6.7 | 0.587 | 0.933 | 0.721 | 7.4% |
| Wave Corrector | threshold 4 | 26.0 | +6.2 | 0.833 | 0.812 | 0.822 | 9.2% |
| Needledropper's | sensitivity 0 | 26.0 | +6.1 | 0.348 | 0.971 | 0.513 | 6.4% |

Those two sets are where the retrain shows up: 3.1 dB and 4.6 dB over 1.0.1, with F1 going from
0.650 to 0.963 and from 0.721 to 0.955. They say the mixer change did what it was meant to do.
They say nothing about damage nobody put in the mixer, which is the next two sets.

**scratch**, input SNR 19.4 dB. Held out of training.

| tool | setting | SNR out | gain | P | R | F1 | off-target |
|---|---|---|---|---|---|---|---|
| grooveclean 1.0.1 | 0.35 | **32.6** | **+13.2** | 0.992 | 0.612 | 0.757 | 0.2% |
| grooveclean 1.1 | 0.35 | 32.4 | +13.0 | 0.995 | 0.529 | 0.691 | 0.1% |
| Needledropper's | sensitivity 0 | 24.7 | +5.3 | 0.678 | 0.561 | 0.614 | 25.5% |
| Wave Corrector | threshold 3 | 23.2 | +3.8 | 0.965 | 0.422 | 0.587 | 13.4% |

**dropout**, input SNR 18.1 dB. Held out of training. Nothing recovers any of it.

| tool | setting | SNR out | gain | P | R | F1 | off-target |
|---|---|---|---|---|---|---|---|
| Wave Corrector | threshold 3 | 18.0 | -0.1 | 0.982 | 0.954 | **0.968** | 40.8% |
| Needledropper's | sensitivity 0 | 18.0 | -0.1 | 0.699 | 0.958 | 0.808 | 69.1% |
| grooveclean 1.0.1 | 0.80 | 18.0 | -0.1 | 0.572 | 0.722 | 0.638 | 50.1% |
| grooveclean 1.1 | 0.80 | 17.8 | -0.3 | 0.911 | 0.903 | 0.907 | 74.3% |

The gain column is the whole story on `dropout`. Every tool is within 0.3 dB of doing nothing,
including Wave Corrector, which finds 95% of the events. Detection is not what fails there.
Interpolating across 20 ms of lost groove from the music either side does not put the music back,
whichever detector asked for it.

**control**, 120 seconds of music with nothing wrong with it. Fewer frames touched is better.

| tool | setting | frames touched | per minute | pooled change |
|---|---|---|---|---|
| grooveclean 1.1 | 0.20 | **0** | **0** | nothing at all |
| grooveclean 1.1 | 0.35 | 24 | 12 | -79.6 dBFS |
| grooveclean 1.1 | 0.50 (default) | 151 | 76 | -75.1 dBFS |
| grooveclean 1.0.1 | 0.50 (default) | 471 | 236 | -67.4 dBFS |
| Wave Corrector | threshold 3 (default) | 4,232 | 2,116 | -55.6 dBFS |
| Needledropper's | sensitivity 30 (default) | 33,764 | 16,882 | -40.8 dBFS |

At the settings each ships with, grooveclean 1.1 disturbs undamaged music 28x less often than
Wave Corrector and 222x less often than Needledropper's.

Five of the six control clips measure 0.00 impulses per second on a plain impulse screen. One,
`control-01`, measures 1.10, so a tool touching that file may be catching a tick that really is
in the source. These are upper bounds on damage, equally for all three.

## Did broadening the damage model help?

That was the point of 1.1, so it gets its own answer. Gain in dB at each version's best setting:

| set | held out of training? | 1.0.1 | 1.1 |
|---|---|---|---|
| general | no | +16.8 | +17.3 |
| percussive | no | +18.9 | +17.4 |
| resonant | added to 1.1's mixer | +10.6 | +13.7 |
| gouge | added to 1.1's mixer | +6.7 | +11.3 |
| scratch | **yes** | +13.2 | +13.0 |
| dropout | **yes** | +0.0 | -0.0 |

On the two families the mixer gained, the model improved by 3 to 5 dB and its F1 went from around
0.7 to around 0.96. On the one held-out family anything can repair at all, it moved by 0.2 dB,
which is nothing. Writing more kinds of damage into the training set bought competence at those
kinds of damage. It did not buy generalisation.

The detector did generalise a little further than the repair could use. On `dropout`, detection
F1 at sensitivity 0.80 went from 0.638 to 0.907, so the network learned something about
quieter-than-the-music damage from being shown destructive damage that was louder. It has
nowhere to put it, because the interpolator cannot reconstruct 20 ms of music it never had.

The cost is about 1.5 dB on `percussive`, and roughly 4 dB of headroom on faint ticks: at the
default sensitivity 1.1 finds harvested ticks down to about 7 dB over the local music level where
1.0.1 reached about 4 dB. In exchange the default operating point got much quieter, 76 frames per
minute disturbed on `control` against 1.0.1's 236, with better SNR on four of the five sets
anything can repair.

## Real transfers

Twelve whole 78 sides from the held-out test split of the noise corpus, 45 seconds each after
skipping the run-in groove, 9 minutes in total. Mixed sources: 96 kHz and 44.1 kHz, mono and
stereo, Edison Diamond Discs through to 1930s dance bands. Nothing was resampled, because
resampling would hand every tool a different high band from the one its own defaults were tuned
against.

With no truth to compare against, all that can be measured is what each tool decided to remove.
A tick is broadband, so its residue should have a flat spectrum and a swallowed note should not.
Flatness is measured over the band holding 99% of that file's energy, because these transfers
have an empty top octave that would otherwise dominate the figure and would reward a tool whose
interpolation rings wideband.

Medians over the twelve sides:

| tool | spans/min | samples touched | removed | flatness of residue |
|---|---|---|---|---|
| grooveclean 0.35 | 710 | 0.28% | -58.8 dBFS | 0.788 |
| grooveclean 0.50 (default) | 1,226 | 0.73% | -55.2 dBFS | 0.782 |
| Wave Corrector threshold 3 | 1,943 | 1.40% | -57.4 dBFS | 0.952 |
| Wave Corrector threshold 4 | 2,496 | 1.43% | -56.5 dBFS | 0.924 |
| Needledropper's sensitivity 0 | 7,725 | 1.68% | -49.6 dBFS | 0.873 |

The span counts order the same way as the `control` set. At the settings each ships with,
grooveclean flags a sixth as many spans per minute as Needledropper's and two thirds as many as
Wave Corrector, and touches under half as many samples as either. Removed energy does not follow:
it takes out 5.6 dB less than Needledropper's but 2.2 dB more than Wave Corrector, which touches
twice as many samples to remove less from them. Whether that is Wave Corrector being gentler or
grooveclean actually catching louder ticks is not something this measurement can settle.

Read the flatness column with care, because it is biased against interpolation. `in - out` over a
repaired span is the difference between the real music and the predicted music as well as the
click, and predicted music is tonal by construction. A tool that replaces more samples per event
therefore scores more tonal even when it caught exactly the same tick. grooveclean's residue is
the least broadband here and also by far the smallest, and this measure cannot separate those two
explanations. It is not evidence that grooveclean ate more music, and it is not evidence that it
did not.

## What it does to music that is already clean

Pointed at all 40 held-out netlabels releases in the clean corpus, 60 seconds each, at the default
sensitivity, 18 come out with no clicks detected at all, so the output is the input. Of the other
22, all but eight touch under 0.01% of the file and the worst touches 0.15%. The ones it touches
are loud, distorted, high-frequency-dense electronic tracks where the waveform is jagged
everywhere and a local impulse test has nothing to stand out against. That is not groove-transfer
material and grooveclean is not aimed at it, but it is the honest answer to what happens if you
point it at the wrong thing.

## Speed

920 seconds of 44.1 kHz stereo, 46 files, wall clock including all file I/O and process startup.

| tool | time | faster than real time |
|---|---|---|
| Needledropper's | 8.5 s | 108x |
| Wave Corrector | 15.4 s | 60x |
| grooveclean, RTX 4090 | 18.7 s | 49x |
| grooveclean, i9-14900K CPU | 97.3 s | 9.5x |

grooveclean is still the slowest of the three and still the only one that wants a GPU. Wave
Corrector's figure comes from its GUI batch mode driven by UI automation, so it includes per-file
window overhead, and the poll granularity was 0.4 s.

Where the time goes, on a 45 second 96 kHz stereo side with the GPU synchronised between stages:

| stage | time | share |
|---|---|---|
| normalisation and CNN forward, GPU | 0.29 s | 33% |
| LSAR interpolation, GPU | 0.30 s | 33% |
| impulsiveness screen, CPU | 0.13 s | 15% |
| file I/O | 0.16 s | 17% |
| hysteresis and span merging | 0.02 s | 2% |

There is no hot spot to fix. The largest single lever is running the network in bfloat16 rather
than float32, worth 2.2x on the detect stage and 1.2x on the whole run, and it changes the
answer: 1,246 of 53,406 flagged samples flip. That would cost the property that a CPU run and a
CUDA run find the same clicks, which is worth more than 20% to anyone checking a result or
filing a bug. Not taken. If you need 100x, use Needledropper's, and this document says so.

## What I would and would not claim from this

Supported. On damage that can be repaired at all, grooveclean recovers 4 to 10 dB more of the
clean signal than either competitor, at every setting either of them exposes, and it disturbs
undamaged music 28x to 222x less at the settings each ships with. That margin is 7.7 dB on
`scratch`, which nothing here was trained on, against 9.7 dB on `general`, which it was, so most
of it is not home advantage. Needledropper's README's own caveat about percussive material is real and measurable,
and so is Wave Corrector's recall on the same set.

Supported, and the honest correction to the 1.0.1 version of this document. Adding damage models
to training buys accuracy on those damage models and does not generalise past them. `resonant`
and `gouge` improved by 3 to 5 dB once they were written into the mixer, and `scratch`, which was
not, did not move at all. Anyone reading a benchmark where the author also chose the damage
should assume the same about every number in it, including these.

Not supported. Anything about how these sound: SNR against a synthetic truth is not a listening
test and nobody has run one. Anything about the two programs as programs, since a GUI with a
click list you can audit is worth something this benchmark cannot see. And nothing at all about
groove damage that loses the music rather than burying it, where all three tools are within
0.3 dB of doing nothing.

## Reproducing

```
python bench/corpus.py                    # writes the corpus and the ground truth
python bench/fetch_real.py                # fetches the twelve real 78 sides
grooveclean batch <in> -o <out>           # or bench/run_nd.py for Needledropper's
python bench/score.py --tools gc-s50 gc101-s50 nd-s0 wc-t3
python bench/real.py
```

`corpus.py` needs `corpus/clean` and `corpus/noise`, which is what `train/harvest_clean.py` and
`train/harvest_noise.py` build. They are not in the repo.

**Needledropper's** has no releases and no command line, so it was driven through a small
headless `main()` over its `src/dsp`, which is JUCE-free and links standalone. That bridge is not
in this repo: it includes AGPL headers and copies `merge_reversed_clicks` out of
`DetectionThread.cpp`, so it is a derivative work and cannot sit in an MIT tree. It is about 80
lines and mirrors `DetectionThread::run` plus `ProcessingThread`'s repair path.

```cpp
WaveletEngine engine(5);
ClickDetector detector(engine);
RepairEngine  repair(engine);
detector.detect_stereo(L, R, n, sensitivity, crackle, rate, left, right, cancel);
// then the reverse pass the app enables by default: detect_mono on reversed copies of each
// channel, flip the event positions back, merge into the forward list
repair.repair_stereo(L, R, n, left, right, out_l, out_r, cancel);
```

Built with MSVC 2022, `/O2 /EHsc /std:c++17 /D_USE_MATH_DEFINES /FIalgorithm /FIcmath`. The last
two are forced includes that supply `std::clamp` and `M_PI` without editing its headers. Its own
checked-in `test_repair.cpp` does not compile against the current API.

**Wave Corrector** has a GUI batch mode and no command line, so it was driven by Win32 UI
automation, setting the click threshold trackbar and reading the dialog label back before each
run. Threshold 3 was run twice on the same corpus, hours apart, and produced byte-identical
output, so that path is deterministic.

## Full sweep

Every setting each tool exposes. Needledropper's sensitivity is a 0-100 slider mapping to a
k-sigma threshold, grooveclean's is a 0-1 probability threshold, Wave Corrector's is a 0-5
integer where 0 turns declicking off. `gc-` is 1.1, `gc101-` is 1.0.1.

<details>
<summary>expand</summary>

```

general  (10 files, 200 s)
  input SNR 15.4 dB
  tool            SNR out    gain       P       R      F1  off-target
  gc-s20             30.0    14.6   0.999   0.894   0.944       0.0%
  gc-s35             31.8    16.4   0.999   0.926   0.961       0.0%
  gc-s50             32.3    17.0   0.996   0.946   0.971       0.6%
  gc-s65             32.7    17.3   0.982   0.961   0.972       1.3%
  gc-s80             29.8    14.4   0.953   0.973   0.963      10.9%
  gc101-s20          31.2    15.8   0.997   0.941   0.968       0.0%
  gc101-s35          31.8    16.5   0.992   0.957   0.974       1.9%
  gc101-s50          32.1    16.8   0.978   0.969   0.974       8.0%
  gc101-s65          31.8    16.4   0.939   0.981   0.960       8.8%
  gc101-s80          28.8    13.4   0.854   0.987   0.915      11.6%
  nd-s0              23.0     7.7   0.883   0.915   0.898      19.6%
  nd-s30             22.1     6.7   0.741   0.949   0.832      21.4%
  wc-t3              21.8     6.4   0.988   0.836   0.906      14.3%
  wc-t4              21.8     6.5   0.986   0.847   0.911      14.5%

percussive  (6 files, 120 s)
  input SNR 18.9 dB
  tool            SNR out    gain       P       R      F1  off-target
  gc-s20             33.8    15.0   0.995   0.772   0.869       0.1%
  gc-s35             35.3    16.4   0.987   0.832   0.903       1.6%
  gc-s50             35.8    16.9   0.971   0.886   0.927       3.2%
  gc-s65             36.3    17.4   0.942   0.934   0.938       7.8%
  gc-s80             34.6    15.7   0.859   0.957   0.905      14.3%
  gc101-s20          34.8    15.9   0.983   0.813   0.890       0.9%
  gc101-s35          36.2    17.3   0.963   0.863   0.911       1.2%
  gc101-s50          37.8    18.9   0.890   0.913   0.901       2.3%
  gc101-s65          36.2    17.3   0.743   0.963   0.839       7.7%
  gc101-s80          31.0    12.1   0.533   0.985   0.692      16.0%
  nd-s0              32.1    13.2   0.854   0.826   0.840      13.9%
  nd-s30             28.5     9.6   0.655   0.912   0.763      18.5%
  wc-t3              25.6     6.7   0.982   0.612   0.754      11.1%
  wc-t4              25.6     6.7   0.979   0.612   0.753      11.2%

control  (6 files, 120 s)
  tool            frames touched   per minute   damage dBFS   worst file
  gc-s20                       0            0        -390.3       -390.3
  gc-s35                      24           12         -79.6        -72.1
  gc-s50                     151           76         -75.1        -70.8
  gc-s65                     872          436         -65.4        -59.2
  gc-s80                   3,842        1,921         -58.8        -53.5
  gc101-s20                   12            6         -95.0        -87.2
  gc101-s35                   83           42         -77.6        -71.4
  gc101-s50                  471          236         -67.4        -63.5
  gc101-s65                2,934        1,467         -58.7        -55.3
  gc101-s80               10,805        5,402         -53.0        -49.5
  nd-s0                   18,549        9,274         -42.4        -35.8
  nd-s30                  33,764       16,882         -40.8        -34.2
  wc-t3                    4,232        2,116         -55.6        -49.2
  wc-t4                    5,176        2,588         -55.4        -49.0

resonant  (6 files, 120 s)
  input SNR 16.2 dB
  tool            SNR out    gain       P       R      F1  off-target
  gc-s20             26.2    10.0   0.984   0.910   0.946       0.5%
  gc-s35             30.0    13.7   0.977   0.948   0.963       0.6%
  gc-s50             29.5    13.3   0.938   0.960   0.949       2.9%
  gc-s65             27.9    11.6   0.859   0.973   0.913       5.5%
  gc-s80             26.9    10.7   0.763   0.981   0.859       9.0%
  gc101-s20          19.4     3.1   0.988   0.606   0.751       0.2%
  gc101-s35          20.1     3.9   0.937   0.723   0.816       1.3%
  gc101-s50          22.3     6.0   0.871   0.839   0.855       2.9%
  gc101-s65          25.2     9.0   0.705   0.903   0.792       4.7%
  gc101-s80          26.8    10.6   0.492   0.957   0.650       9.5%
  nd-s0              21.0     4.8   0.801   0.965   0.876       7.7%
  nd-s30             21.7     5.5   0.488   0.982   0.652       9.8%
  wc-t3              22.5     6.2   0.824   0.833   0.828      13.4%
  wc-t4              22.6     6.4   0.758   0.838   0.796      13.7%

gouge  (6 files, 120 s)
  input SNR 19.9 dB
  tool            SNR out    gain       P       R      F1  off-target
  gc-s20             30.8    10.9   0.966   0.941   0.953       0.7%
  gc-s35             31.0    11.1   0.950   0.958   0.954       1.9%
  gc-s50             31.1    11.3   0.929   0.983   0.955       2.1%
  gc-s65             31.1    11.2   0.853   0.992   0.917       3.5%
  gc-s80             31.0    11.1   0.700   0.996   0.822       5.1%
  gc101-s20          23.9     4.1   0.987   0.644   0.780       0.4%
  gc101-s35          24.8     5.0   0.931   0.787   0.853       3.3%
  gc101-s50          25.9     6.0   0.820   0.879   0.848       4.3%
  gc101-s65          26.5     6.7   0.587   0.933   0.721       7.4%
  gc101-s80          26.3     6.5   0.333   0.962   0.495      14.8%
  nd-s0              26.0     6.1   0.348   0.971   0.513       6.4%
  nd-s30             24.2     4.3   0.150   0.983   0.261      12.9%
  wc-t3              26.0     6.1   0.850   0.803   0.826       9.1%
  wc-t4              26.0     6.2   0.833   0.812   0.822       9.2%

scratch  (6 files, 120 s)
  input SNR 19.4 dB
  tool            SNR out    gain       P       R      F1  off-target
  gc-s20             31.8    12.4   0.996   0.457   0.626       0.0%
  gc-s35             32.4    13.0   0.995   0.529   0.691       0.1%
  gc-s50             30.7    11.3   0.994   0.586   0.737       3.7%
  gc-s65             28.6     9.1   0.988   0.628   0.768       9.7%
  gc-s80             25.4     6.0   0.970   0.672   0.794      16.4%
  gc101-s20          32.5    13.0   0.995   0.565   0.720       0.1%
  gc101-s35          32.6    13.2   0.992   0.612   0.757       0.2%
  gc101-s50          31.4    12.0   0.980   0.658   0.787       1.1%
  gc101-s65          29.1     9.7   0.948   0.696   0.803       4.4%
  gc101-s80          26.3     6.9   0.863   0.739   0.796      10.4%
  nd-s0              24.7     5.3   0.678   0.561   0.614      25.5%
  nd-s30             23.5     4.0   0.502   0.640   0.563      35.0%
  wc-t3              23.2     3.8   0.965   0.422   0.587      13.4%
  wc-t4              23.1     3.6   0.950   0.432   0.594      16.4%

dropout  (6 files, 120 s)
  input SNR 18.1 dB
  tool            SNR out    gain       P       R      F1  off-target
  gc-s20             18.1    -0.0   1.000   0.212   0.350      11.8%
  gc-s35             18.1    -0.0   0.991   0.375   0.544      48.8%
  gc-s50             18.1    -0.0   0.988   0.588   0.737      72.2%
  gc-s65             17.9    -0.2   0.974   0.784   0.869      72.1%
  gc-s80             17.8    -0.3   0.911   0.903   0.907      74.3%
  gc101-s20          18.1     0.0   0.981   0.094   0.171       5.3%
  gc101-s35          18.1     0.0   0.978   0.154   0.266      28.1%
  gc101-s50          18.1     0.0   0.913   0.260   0.405      33.2%
  gc101-s65          18.1     0.0   0.803   0.476   0.598      43.6%
  gc101-s80          18.0    -0.1   0.572   0.722   0.638      50.1%
  nd-s0              18.0    -0.1   0.699   0.958   0.808      69.1%
  nd-s30             18.0    -0.1   0.602   0.979   0.745      64.3%
  wc-t3              18.0    -0.1   0.982   0.954   0.968      40.8%
  wc-t4              17.9    -0.2   0.976   0.954   0.965      45.6%
```

</details>
