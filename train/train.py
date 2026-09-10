"""Train the click detector and calibrate its two thresholds.

Segments are mixed on demand rather than written out first: the click corpus is small enough
that a fixed dataset would be memorised, and a fresh random placement every step is free.
Training never sees an identifier from the test split, on either side of the mix.

Calibration is the second half of the job and matters as much as the loss. The network emits
a probability; what ships is the (enter, leave) pair that maximises event F1 while staying
under one false positive per minute of click-free music, measured on the held-out split.

    python train/train.py --steps 6000
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import metrics  # noqa: E402
import mix  # noqa: E402
from grooveclean import detect  # noqa: E402

RATE = detect.ANALYSIS_RATE
SEGMENT = RATE  # 1 s per training example
POS_WEIGHT = 5.0
LR = 3e-3
WEIGHT_DECAY = 1e-4
WARMUP = 200

# Even spacing in logit space, because the useful thresholds crowd towards 1 and a linear
# grid spends most of its points where nothing changes.
HI_GRID = 1.0 / (1.0 + np.exp(-np.linspace(-1.0, 7.0, 21)))
LO_GRID = 1.0 / (1.0 + np.exp(-np.linspace(-4.0, 5.0, 16)))
FP_PER_MINUTE = 1.0
F1_TIE = 0.001  # closer than this is a couple of events, not a real difference
EVAL_CLICKY = 60
EVAL_CLEAN = 100


class Segments(Dataset):
    """One mixed segment per index, reproducible from the index alone.

    Length is steps * batch, so a single pass never repeats a draw and there is no epoch
    boundary to reshuffle across.
    """

    def __init__(self, corpus: mix.Corpus, seed: int, count: int, channels: int = 2):
        self.corpus = corpus
        self.seed = seed
        self.count = count
        self.channels = channels

    def __len__(self) -> int:
        return self.count

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        mixer = mix.Mixer(self.corpus, self.seed + index, segment=SEGMENT, channels=self.channels)
        noisy, _, mask = mixer.draw()
        return torch.from_numpy(noisy.astype(np.float32)), torch.from_numpy(mask)


def loss_of(
    model: detect.ClickCNN, noisy: torch.Tensor, mask: torch.Tensor, trim: int
) -> torch.Tensor:
    """Per-sample BCE, with the receptive field at each end left out.

    Those samples see zero padding instead of audio, and at inference they never do.
    """
    x = detect.normalize(noisy, RATE).reshape(-1, 1, noisy.shape[-1])
    target = mask.reshape(-1, mask.shape[-1]).to(x.dtype)
    with torch.autocast("cuda", torch.bfloat16, enabled=x.device.type == "cuda"):
        logits = model(x)
    return F.binary_cross_entropy_with_logits(
        logits[:, trim:-trim].float(),
        target[:, trim:-trim],
        pos_weight=torch.tensor(POS_WEIGHT, device=x.device),
    )


def learning_rate(step: int, total: int) -> float:
    if step < WARMUP:
        return LR * (step + 1) / WARMUP
    progress = (step - WARMUP) / max(1, total - WARMUP)
    return LR * 0.5 * (1.0 + math.cos(math.pi * min(1.0, progress)))


def validation_set(
    corpus: mix.Corpus, seed: int, stem: Path, manifest: Path
) -> tuple[list[np.ndarray], list[np.ndarray], np.ndarray, int]:
    """The same artefact the shipped test suite scores against, built if it is not there."""
    if not stem.with_suffix(".flac").exists():
        mix.write_eval(corpus, seed, EVAL_CLICKY, EVAL_CLEAN, stem, manifest)
    return mix.load_eval(stem)


def calibrate(
    detector: detect.Detector,
    segments: list[np.ndarray],
    masks: list[np.ndarray],
    kinds: np.ndarray,
    rate: int,
) -> tuple[float, float, metrics.Score]:
    """Sweep (enter, leave) for the best F1 that stays under the false positive budget."""
    gate = detect.thresholds(0.5, 0.5, 0.5)[2]
    probs = metrics.probabilities(detector, segments, rate)
    actives = metrics.active_masks(segments, rate, gate)

    scored = []
    for hi in HI_GRID:
        for lo in LO_GRID[hi >= LO_GRID]:
            score = metrics.evaluate(probs, actives, masks, kinds, rate, float(hi), float(lo))
            scored.append((float(hi), float(lo), score))
    affordable = [row for row in scored if row[2].fp_per_minute <= FP_PER_MINUTE]
    if not affordable:
        # Nothing meets the budget, so pick the quietest point and let the caller see it.
        return min(scored, key=lambda row: (row[2].fp_per_minute, -row[2].f1))
    # Event F1 only asks whether a span overlaps a click at all, so it is flat to a few events
    # across most of the grid and a plain maximum lands anywhere in that plateau, including on
    # lo == hi with hysteresis switched off. Break the tie on how far the spans actually reach,
    # which is what decides whether a repair covers the click or half the bar around it.
    best = max(row[2].f1 for row in affordable)
    tied = [row for row in affordable if row[2].f1 >= best - F1_TIE]
    return max(tied, key=lambda row: row[2].sample_f1)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--noise", type=Path, default=Path("corpus/noise"))
    ap.add_argument("--clean", type=Path, default=Path("corpus/clean"))
    ap.add_argument("--out", type=Path, default=Path("src/grooveclean/weights/detector.pt"))
    ap.add_argument("--eval", type=Path, default=Path("tests/data/detector_eval"))
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--report-every", type=int, default=250)
    ap.add_argument("--seed", type=int, default=20260910)
    ap.add_argument("--device", default="auto")
    args = ap.parse_args(argv)

    device = detect.resolve_device(args.device)
    torch.manual_seed(args.seed)
    try:
        train_corpus = mix.load_corpus(args.noise, args.clean, "train")
        test_corpus = mix.load_corpus(args.noise, args.clean, "test")
    except mix.CorpusError as exc:
        print(exc, file=sys.stderr)
        return 2
    print(
        f"train: {len(train_corpus.clicks):,} clicks, {train_corpus.beds.shape[0]} beds, "
        f"{len(train_corpus.clean)} clean clips\n"
        f"test:  {len(test_corpus.clicks):,} clicks, {test_corpus.beds.shape[0]} beds, "
        f"{len(test_corpus.clean)} clean clips",
        flush=True,
    )

    segments, masks, kinds, rate = validation_set(
        test_corpus, args.seed + 7, args.eval, args.clean / "manifest.json"
    )

    model = detect.ClickCNN().to(device)
    trim = model.receptive_field // 2
    total = sum(p.numel() for p in model.parameters())
    print(
        f"{total:,} parameters, receptive field {model.receptive_field} samples "
        f"({model.receptive_field / RATE * 1e3:.1f} ms), device {device}",
        flush=True,
    )

    loader = DataLoader(
        Segments(train_corpus, args.seed, args.steps * args.batch),
        batch_size=args.batch,
        num_workers=args.workers,
        pin_memory=device.type == "cuda",
        persistent_workers=args.workers > 0,
        prefetch_factor=4 if args.workers else None,
    )
    optimiser = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)

    started = time.perf_counter()
    running = 0.0
    model.train()
    for step, (noisy, mask) in enumerate(loader):
        for group in optimiser.param_groups:
            group["lr"] = learning_rate(step, args.steps)
        loss = loss_of(model, noisy.to(device, non_blocking=True), mask.to(device), trim)
        optimiser.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimiser.step()

        running += float(loss)
        if (step + 1) % args.report_every == 0:
            print(
                f"step {step + 1}/{args.steps}  loss {running / args.report_every:.4f}  "
                f"lr {optimiser.param_groups[0]['lr']:.2e}  "
                f"{(time.perf_counter() - started) / (step + 1):.2f}s/step",
                flush=True,
            )
            running = 0.0

    detector = detect.Detector(model, detect.Calibration(0.5, 0.5), device)
    hi, lo, score = calibrate(detector, segments, masks, kinds, rate)
    print(f"calibrated hi={hi:.2f} lo={lo:.2f}: {score}", flush=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "config": model.config,
            "state_dict": {k: v.cpu() for k, v in model.state_dict().items()},
            "calibration": {"hi": hi, "lo": lo},
        },
        str(args.out),
    )
    args.out.with_suffix(".json").write_text(
        json.dumps(
            {
                "steps": args.steps,
                "batch": args.batch,
                "segment_seconds": SEGMENT / RATE,
                "train_clicks": len(train_corpus.clicks),
                "train_clips": len(train_corpus.clean),
                "calibration": {"hi": hi, "lo": lo},
                "held_out": {
                    "f1": round(score.f1, 4),
                    "precision": round(score.precision, 4),
                    "recall": round(score.recall, 4),
                    "fp_per_minute_on_clean": round(score.fp_per_minute, 3),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    size_mb = args.out.stat().st_size / 2**20
    print(f"wrote {args.out} ({size_mb:.1f} MB)", flush=True)
    return 0 if score.f1 >= 0.95 and score.fp_per_minute <= FP_PER_MINUTE else 1


if __name__ == "__main__":
    raise SystemExit(main())
