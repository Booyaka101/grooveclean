"""Event-level scoring for the detector, shared by the calibration sweep and the test suite.

A click is an event, not a set of samples. A prediction counts if it overlaps a real click at
all, because a tick two samples short at one edge is still a caught tick. False positives are
counted separately on click-free music, since that is the number that decides whether the
tool is safe to point at a whole collection.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from grooveclean import detect  # noqa: E402


def runs(mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Contiguous True runs as (starts, ends)."""
    starts, ends, _ = detect.hysteresis(mask.astype(np.float32), 0.5, 0.5)
    return starts, ends


def hits(
    a_starts: np.ndarray, a_ends: np.ndarray, b_starts: np.ndarray, b_ends: np.ndarray
) -> np.ndarray:
    """Per span in a, whether it overlaps any span in b. Both sets sorted and disjoint."""
    if a_starts.size == 0:
        return np.zeros(0, dtype=bool)
    if b_starts.size == 0:
        return np.zeros(a_starts.size, dtype=bool)
    # The first b that has not already ended is the only one that can overlap.
    at = np.searchsorted(b_ends, a_starts, side="right")
    inside = at < b_starts.size
    out = np.zeros(a_starts.size, dtype=bool)
    out[inside] = b_starts[at[inside]] < a_ends[inside]
    return out


def covered(starts: np.ndarray, ends: np.ndarray, length: int) -> np.ndarray:
    """Flatten disjoint spans back into a sample mask."""
    edges = np.zeros(length + 1, dtype=np.int8)
    edges[starts] += 1
    edges[ends] -= 1
    return np.cumsum(edges[:-1]) > 0


@dataclass(slots=True)
class Score:
    tp: int = 0
    fp: int = 0
    fn: int = 0
    clean_fp: int = 0
    clean_seconds: float = 0.0
    tp_samples: int = 0
    fp_samples: int = 0
    fn_samples: int = 0

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if self.tp + self.fp else 1.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if self.tp + self.fn else 1.0

    @property
    def f1(self) -> float:
        denominator = 2 * self.tp + self.fp + self.fn
        return 2 * self.tp / denominator if denominator else 1.0

    @property
    def sample_f1(self) -> float:
        """Event F1 with the spans' extent counted, which event F1 by design ignores."""
        denominator = 2 * self.tp_samples + self.fp_samples + self.fn_samples
        return 2 * self.tp_samples / denominator if denominator else 1.0

    @property
    def fp_per_minute(self) -> float:
        return self.clean_fp / (self.clean_seconds / 60.0) if self.clean_seconds else 0.0

    def __str__(self) -> str:
        return (
            f"F1 {self.f1:.4f}  P {self.precision:.4f}  R {self.recall:.4f}  "
            f"{self.fp_per_minute:.2f} FP/min on clean ({self.clean_fp} in "
            f"{self.clean_seconds:.0f} s)"
        )


def probabilities(
    detector: detect.Detector, segments: list[np.ndarray], rate: int
) -> list[np.ndarray]:
    return [
        detector.probabilities(torch.from_numpy(seg[None, :].astype(np.float32)), rate)[0]
        .cpu()
        .numpy()
        for seg in segments
    ]


def active_masks(segments: list[np.ndarray], rate: int, gate: float) -> list[np.ndarray]:
    """Cached separately from `evaluate` because a threshold sweep does not change it."""
    return [detect.active_mask(seg, rate, gate) for seg in segments]


def evaluate(
    probs: list[np.ndarray],
    actives: list[np.ndarray],
    masks: list[np.ndarray],
    kinds: np.ndarray,
    rate: int,
    hi: float,
    lo: float,
) -> Score:
    """Score one (hi, lo) pair. `kinds` marks each segment 1 for clicky, 0 for clean music."""
    score = Score()
    for prob, active, mask, kind in zip(probs, actives, masks, kinds, strict=True):
        starts, ends, _ = detect.spans(prob, active, rate, hi, lo)
        if not kind:
            score.clean_fp += int(starts.size)
            score.clean_seconds += mask.size / rate
            continue
        true_starts, true_ends = runs(mask)
        found = hits(true_starts, true_ends, starts, ends)
        score.tp += int(found.sum())
        score.fn += int((~found).sum())
        score.fp += int((~hits(starts, ends, true_starts, true_ends)).sum())
        taken = covered(starts, ends, mask.size)
        real = mask.astype(bool)
        score.tp_samples += int((taken & real).sum())
        score.fp_samples += int((taken & ~real).sum())
        score.fn_samples += int((~taken & real).sum())
    return score
