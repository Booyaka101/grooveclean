# Standalone detector hardening, October 2026

This is an incremental safety change, not a retrained model or evidence that arbitrary
full-band music is now reliably separable from groove clicks. The weights remain unchanged.

## Decision and measured cost

Require integrated squared impulse excess over the native gate, normalized to 44.1 kHz
sample units. At default sensitivity, a single sample with impulsiveness 5 suffices, but
several weaker samples can provide the same evidence. Clipped samples contribute nothing.
Reject insufficiently supported events without extending their repair boundaries.

| Legacy evaluation | Released pipeline | With event support |
| --- | ---: | ---: |
| Event F1 | 0.994408 | 0.992994 |
| Recall | 0.990255 | 0.986543 |
| Precision | about 0.999 | 0.999530 |
| False detections in 200 seconds of clean evaluation audio | 0 | 0 |

The production implementation reproduces the candidate's F1 and recall. Sample F1 is
0.889553 with event support. These sources were held out of weight training, but this
artifact was used for threshold selection and development. It is not a fresh blind test.

A stronger peak-only impulse gate of 5 reached recall 0.985151 and F1 0.992520. Distributed
support retains more true clicks at the same development-noise rejection level.

## Challenge controls

On separate 60-second, peak-0.5 pink and white noise controls, seed 20261029, the released
complete pipeline found 4 and 2 events. The support candidate found zero in both. These
controls informed the change and are development data.

Regression tests use seed 20261030 and pair each 60-second control with the same audio plus
12 known single-sample impulses. At default sensitivity, each negative control must stay
within one detection per minute, and the positive must recover at least 95% of the injected
events. Separate tests check native-rate localization at 22.05, 48, 96 and 192 kHz, short
inputs, clipping exclusion, support integration and parity between the public event API and
the CLI decision helper.

The golden-excerpt candidate count moves from 1,184 to 1,174. The existing 2% count tolerance
is unchanged; this is a regression check, not a labeled measure of detection quality.

Run the checked-in controls offline:

```sh
python -m pytest tests/test_detection_safety.py tests/test_detector.py tests/test_golden.py
python -m pytest tests/test_training_splits.py
```

## Calibration isolation

Future training preserves historical test identifiers in hash bucket 0, reserves bucket 1
for calibration, and uses the rest for training. New evaluation artifacts record both clean
and noise source pools. Calibration refuses missing or wrong-split provenance. Final tests
reject known wrong-split sources and explicitly label historical artifacts without provenance.
Calibration and final-test paths cannot alias the same FLAC/NPZ artifact. The mixer defaults
to a different output path for each split. Both calibration and final-test quality gates must
pass; no gate or golden reference was relaxed.

These calibration sources were not held out from the existing weights. The isolation claim
applies to future training runs, not retroactively to the shipped model.

## Existing real-recording controls

The first 60 seconds, or the available shorter length, of each of the 40 existing test-source
clean-corpus recordings were scored at default sensitivity. Total audio duration was
2,390.15 seconds, or 4,600.30 channel-seconds. These recordings passed the corpus's heuristic
impulse screen, but are not independently labeled click-free.

| Complete native-rate detection | Released pipeline | With event support |
| --- | ---: | ---: |
| Events across channels | 476 | 456 |
| Detected channel-samples at 44.1 kHz | 13,332 | 13,244 |
| Recordings with no detected events | 18 | 19 |

This is only a 4.2% reduction in event count and a 0.66% reduction in detected duration.
Some recordings still produce dozens of detections. Without independent labels, these
cannot all be called false positives or removed artifacts. The result does not establish a
solution for dense full-band music; it limits the scope of the stochastic-control improvement.

## Remaining limits

The exact dense-rock recording reported downstream was unavailable. No exact reproduction,
independently labeled real-world evaluation, retraining or listening-panel validation was
completed in this pass. Some faint clicks are intentionally sacrificed; greater sensitivity
can recover more but also admits more false detections. Review the difference file before
accepting repairs on full-band distorted or high-frequency-dense music.
