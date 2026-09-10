# Declicker bake-off

grooveclean's own accuracy numbers are measured against grooveclean's own test set, which
proves it is internally consistent and nothing else. This is the head to head: the same audio
through three declickers, scored the same way, with the corpus builder and the harness in this
folder so you can disagree with the method rather than with me.

Run on 2026-09-10, Windows 11, i9-14900K, RTX 4090.

## What is being compared

| | version | detection | licence |
|---|---|---|---|
| grooveclean | 1.0.1 | dilated 1-D CNN, 84,865 params, 46 ms receptive field | MIT |
| [Needledropper's Declicker](https://github.com/keithhanlon/NeedledroppersDeclick) | `815171c`, 2026-03-30 | AR prediction error on Daubechies D4 detail levels, MAD sigma | AGPL-3.0 |
| [Wave Corrector PE](https://www.wavecor.co.uk/) | 3.9 | not published | freeware, closed source |

Only the declicker is exercised. Both competitors are more than that. Needledropper's has a
click-by-click review GUI, and Wave Corrector is a whole restoration suite with de-hiss, hum
filters, track splitting and CD burning. Wave Corrector's other stages were switched off and
Needledropper's DSP core was driven headless. Neither program was asked to do anything it does
not do at the press of one button.

## The corpus

34 files, 20 seconds each, 16-bit 44.1 kHz stereo, built by `corpus.py` from
[the training mixer](../train/mix.py) over the held-out **test** split. No clean clip and no
harvested click used below was seen during training.

Two departures from how grooveclean's own eval is built, both chosen against my own tool:

- **No 78 lowpass.** The training mixer rolls the music off between 4 and 16 kHz to imitate a
  shellac transfer. The other two are vinyl tools, so the corpus is left full band, which is the
  condition grooveclean is least tuned for.
- **Stereo, not mono.** Both competitors have cross-channel logic that mono would switch off.

| set | files | what it is |
|---|---|---|
| `general` | 10 | arbitrary test-split music, clicks harvested from real 78 transfers |
| `percussive` | 6 | the test-split clips with the highest onset density, same clicks |
| `control` | 6 | the same music with no clicks injected at all |
| `unseen-add` | 6 | clicks that are **not** from the harvested bank: synthesised damped resonances |
| `unseen-gouge` | 6 | the same resonances **replacing** the samples instead of adding to them |

`percussive` exists because Needledropper's own README concedes the case: "On drum-heavy
recordings, AR prediction errors from drum transients are indistinguishable from vinyl clicks at
the signal level. This is a fundamental property of the autoregressive detection approach."

`unseen-add` and `unseen-gouge` exist because of the home advantage. The first three sets come
out of grooveclean's mixer and grooveclean's click bank, so grooveclean has seen that exact
artefact family and the other two have not. The unseen sets use a damage model nothing here was
trained on, and a destructive one that no additive click model covers at all. They are where the
honest margin is.

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
better except off-target.

**general**, input SNR 19.9 dB

| tool | setting | SNR out | gain | P | R | F1 | off-target |
|---|---|---|---|---|---|---|---|
| grooveclean | 0.50 (default) | **40.4** | **+20.6** | 0.976 | 0.975 | **0.976** | 0.0% |
| Needledropper's | sensitivity 0 | 32.8 | +12.9 | 0.962 | 0.900 | 0.930 | 11.0% |
| Wave Corrector | threshold 5 | 29.2 | +9.4 | 0.988 | 0.850 | 0.914 | 8.4% |

**percussive**, input SNR 17.0 dB

| tool | setting | SNR out | gain | P | R | F1 | off-target |
|---|---|---|---|---|---|---|---|
| grooveclean | 0.50 (default) | **43.3** | **+26.3** | 0.995 | 0.997 | **0.996** | 0.1% |
| Needledropper's | sensitivity 0 | 34.6 | +17.7 | 0.872 | 0.994 | 0.929 | 3.5% |
| Wave Corrector | threshold 3 (default) | 25.3 | +8.3 | 0.979 | 0.964 | 0.971 | 9.2% |

Needledropper's precision falls from 0.962 to 0.872 moving from `general` to `percussive` while
its recall goes up, which is its README's own limitation showing up in the numbers. At its
shipped sensitivity of 30 the same figure is 0.725.

**unseen-add**, input SNR 18.1 dB. Damage waveforms nothing was trained on.

| tool | setting | SNR out | gain | P | R | F1 | off-target |
|---|---|---|---|---|---|---|---|
| grooveclean | 0.50 | **31.1** | **+13.0** | 0.964 | 0.953 | **0.958** | 0.3% |
| Wave Corrector | threshold 3 | 27.0 | +8.9 | 0.893 | 0.970 | 0.930 | 7.1% |
| Needledropper's | sensitivity 0 | 23.3 | +5.2 | 0.630 | 0.994 | 0.772 | 9.8% |

**unseen-gouge**, input SNR 20.3 dB. Samples destroyed rather than added to.

| tool | setting | SNR out | gain | P | R | F1 | off-target |
|---|---|---|---|---|---|---|---|
| grooveclean | 0.35 | 23.9 | +3.6 | 0.921 | 0.934 | **0.928** | 2.1% |
| grooveclean | 0.50 | **25.3** | **+5.0** | 0.860 | 0.966 | 0.910 | 2.2% |
| Wave Corrector | threshold 3 | 23.5 | +3.2 | 0.859 | 0.957 | 0.905 | 25.5% |
| Needledropper's | sensitivity 0 | 22.2 | +1.9 | 0.386 | 0.994 | 0.556 | 34.7% |

**control**, 120 seconds of music with nothing wrong with it. Fewer frames touched is better.

| tool | setting | frames touched | per minute | pooled change |
|---|---|---|---|---|
| grooveclean | 0.35 | **154** | **77** | -74.7 dBFS |
| grooveclean | 0.50 (default) | 859 | 430 | -66.0 dBFS |
| Wave Corrector | threshold 3 (default) | 1,012 | 506 | -66.7 dBFS |
| Wave Corrector | threshold 5 | 2,626 | 1,313 | -64.6 dBFS |
| Needledropper's | sensitivity 0 | 6,535 | 3,268 | -53.6 dBFS |
| Needledropper's | sensitivity 30 (default) | 15,037 | 7,518 | -50.6 dBFS |

Wave Corrector at its two quietest settings is the cleanest thing here, at 74 frames touched.
It buys that with recall: threshold 1 finds half the clicks on `general`.

Five of the six control clips measure 0.00 impulses per second on a plain impulse screen. One,
`control-01`, measures 1.10, so a tool touching that file may be catching a tick that really is
in the source. These are upper bounds on damage, equally for all three.

## Real transfers

Two 10-second 96 kHz 78rpm transfers with real damage and no ground truth. Twenty seconds proves
very little and this section is here for completeness, not as evidence.

With no truth to compare against, all that can be measured is what each tool decided to remove.
A tick is broadband, so its residue should have a flat spectrum and a swallowed note should not.
Flatness is measured over the band holding 99% of that file's energy, because these transfers
have an empty top octave that would otherwise dominate the figure and would reward a tool whose
interpolation rings wideband.

```
demo78.wav        band 0 to 23.1 kHz
  tool                 spans/min  touched  removed dBFS  peak dBFS  flatness
  grooveclean 0.35         9,936    4.85%         -39.0       -0.3     0.596
  Needledropper's 0       17,796    3.65%         -39.1       -0.2     0.781
  Wave Corrector 3         5,970    2.69%         -41.4       +0.5     0.982

excerpt78.wav     band 0 to 18.1 kHz
  tool                 spans/min  touched  removed dBFS  peak dBFS  flatness
  grooveclean 0.35         4,782    2.19%         -48.0      -11.8     0.663
  Needledropper's 0        9,048    1.81%         -48.2      -11.6     0.751
  Wave Corrector 3         2,706    2.89%         -49.7      -11.8     0.630
```

These do not separate the three tools, and where they do the ordering flips between the two
clips. Wave Corrector's residue on `demo78` is the most click-like of the three by this measure
while it also touches the least, and on `excerpt78` it is the least click-like. Read nothing
into it either way.

## Speed

440 seconds of 44.1 kHz stereo, 22 files, wall clock including all file I/O.

| tool | time | faster than real time |
|---|---|---|
| Needledropper's | 4.1 s | 107x |
| Wave Corrector | 8.4 s | 52x |
| grooveclean, RTX 4090 | 10.2 s | 43x |
| grooveclean, i9-14900K CPU | 46.5 s | 9.5x |

grooveclean is the slowest of the three and needs a GPU to be merely comparable. Wave Corrector's
figure comes from its GUI batch mode driven by UI automation, so it includes per-file window
overhead, and the poll granularity was 0.4 s.

## What I would and would not claim from this

Supported. On additive impulsive damage grooveclean recovers 4 to 8 dB more of the clean signal
than either, and it disturbs undamaged music between 6x and 40x less than Needledropper's does at
the settings each ships with. Needledropper's README's own caveat about percussive material is
real and measurable.

Supported but much weaker than the first three sets suggest. On damage nothing was trained on the
margin is 4 dB rather than 8, and on destructive damage it is 1.4 dB with Wave Corrector's F1
within 0.005 of grooveclean's. Roughly half of the apparent advantage on `general` and
`percussive` is home advantage, and that is the most important number in this document.

Not supported. Anything about how these sound: SNR against a synthetic truth is not a listening
test and nobody has run one. Anything about real vinyl, since every synthetic set here is built
from 78 click banks. Anything about the two programs as programs, since a GUI with a click list
you can audit is worth something this benchmark cannot see.

## Reproducing

```
python bench/corpus.py                    # writes the corpus and the ground truth
grooveclean batch <in> -o <out>           # or bench/run_nd.py for Needledropper's
python bench/score.py --tools gc-s50 nd-s0 wc-t3
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
run. Threshold 3 was run twice, once inside the sweep and once on its own, and produced
byte-identical output, so that path is deterministic.

## Full sweep

Every setting each tool exposes. Needledropper's sensitivity is a 0-100 slider mapping to a
k-sigma threshold, grooveclean's is a 0-1 probability threshold, Wave Corrector's is a 0-5
integer where 0 turns declicking off.

<details>
<summary>expand</summary>

```
general  (10 files, 200 s)
  input SNR 19.9 dB
  tool            SNR out    gain       P       R      F1  off-target
  gc-s20             37.0    17.2   0.999   0.935   0.966       0.0%
  gc-s35             39.2    19.3   0.995   0.957   0.976       0.0%
  gc-s50             40.4    20.6   0.976   0.975   0.976       0.0%
  gc-s65             40.0    20.2   0.935   0.989   0.961       0.3%
  gc-s80             37.9    18.0   0.849   0.993   0.915       0.9%
  nd-s0              32.8    12.9   0.962   0.900   0.930      11.0%
  nd-s5              32.8    12.9   0.953   0.908   0.930      11.2%
  nd-s10             32.8    12.9   0.944   0.914   0.929      11.4%
  nd-s20             32.7    12.8   0.910   0.926   0.918      11.9%
  nd-s30             32.3    12.5   0.847   0.939   0.891      13.0%
  nd-s40             31.5    11.7   0.725   0.952   0.823      14.8%
  nd-s50             29.2     9.3   0.502   0.965   0.660      19.7%
  nd-s60             26.4     6.5   0.250   0.978   0.398      26.3%
  nd-s70             21.9     2.1   0.103   0.987   0.186      39.7%
  wc-t1              26.6     6.7   1.000   0.504   0.670       4.8%
  wc-t2              28.1     8.2   1.000   0.621   0.766       4.9%
  wc-t3              29.7     9.8   0.995   0.805   0.890       5.1%
  wc-t4              29.7     9.8   0.994   0.815   0.896       5.5%
  wc-t5              29.2     9.4   0.988   0.850   0.914       8.4%

percussive  (6 files, 120 s)
  input SNR 17.0 dB
  tool            SNR out    gain       P       R      F1  off-target
  gc-s20             40.4    23.5   0.999   0.994   0.997       0.0%
  gc-s35             42.2    25.2   0.999   0.996   0.997       0.0%
  gc-s50             43.3    26.3   0.995   0.997   0.996       0.1%
  gc-s65             43.1    26.1   0.984   0.999   0.991       0.2%
  gc-s80             41.6    24.7   0.963   0.999   0.981       0.8%
  nd-s0              34.6    17.7   0.872   0.994   0.929       3.5%
  nd-s5              34.5    17.6   0.861   0.994   0.922       3.8%
  nd-s10             34.5    17.5   0.839   0.995   0.911       4.1%
  nd-s20             34.5    17.5   0.800   0.994   0.886       4.8%
  nd-s30             34.7    17.7   0.725   0.994   0.839       5.8%
  nd-s40             34.1    17.2   0.598   0.996   0.747       7.3%
  nd-s50             32.5    15.5   0.397   0.998   0.568       9.0%
  nd-s60             28.7    11.7   0.175   0.999   0.298      12.5%
  nd-s70             23.9     6.9   0.065   0.999   0.122      23.4%
  wc-t1              24.1     7.1   0.998   0.814   0.897       8.8%
  wc-t2              24.7     7.7   0.996   0.884   0.937       8.9%
  wc-t3              25.3     8.3   0.979   0.964   0.971       9.2%
  wc-t4              25.1     8.1   0.943   0.970   0.956       9.8%
  wc-t5              25.3     8.3   0.908   0.978   0.942      10.5%

unseen-add  (6 files, 120 s)
  input SNR 18.1 dB
  tool            SNR out    gain       P       R      F1  off-target
  gc-s35             30.4    12.3   0.976   0.901   0.937       0.1%
  gc-s50             31.1    13.0   0.964   0.953   0.958       0.3%
  nd-s0              23.3     5.2   0.630   0.994   0.772       9.8%
  nd-s30             23.0     4.9   0.268   0.994   0.422      16.2%
  wc-t3              27.0     8.9   0.893   0.970   0.930       7.1%
  wc-t5              26.9     8.8   0.801   0.978   0.881       8.2%

unseen-gouge  (6 files, 120 s)
  input SNR 20.3 dB
  tool            SNR out    gain       P       R      F1  off-target
  gc-s35             23.9     3.6   0.921   0.934   0.928       2.1%
  gc-s50             25.3     5.0   0.860   0.966   0.910       2.2%
  nd-s0              22.2     1.9   0.386   0.994   0.556      34.7%
  nd-s30             21.0     0.7   0.171   1.000   0.292      41.3%
  wc-t3              23.5     3.2   0.859   0.957   0.905      25.5%
  wc-t5              23.9     3.6   0.687   0.971   0.805      26.3%

control  (6 files, 120 s)
  tool            frames touched   per minute   damage dBFS   worst file
  gc-s20                      30           15         -80.4        -74.5
  gc-s35                     154           77         -74.7        -69.2
  gc-s50                     859          430         -66.0        -61.3
  gc-s65                   3,758        1,879         -59.4        -54.1
  gc-s80                  15,037        7,518         -53.0        -47.3
  nd-s0                    6,535        3,268         -53.6        -48.4
  nd-s5                    7,273        3,636         -53.2        -47.9
  nd-s10                   8,160        4,080         -52.9        -47.5
  nd-s20                  10,783        5,392         -51.9        -46.7
  nd-s30                  15,037        7,518         -50.6        -45.8
  nd-s40                  24,400       12,200         -48.8        -44.4
  nd-s50                  47,257       23,628         -46.7        -42.1
  nd-s60                 127,657       63,828         -43.1        -37.6
  nd-s70                 415,934      207,967         -38.0        -32.2
  wc-t1                       74           37         -79.5        -71.8
  wc-t2                      206          103         -75.8        -68.0
  wc-t3                    1,012          506         -66.7        -58.9
  wc-t4                    1,408          704         -65.9        -58.1
  wc-t5                    2,626        1,313         -64.6        -57.2
```

</details>
