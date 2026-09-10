"""Score every declicker's output against the corpus ground truth.

The primary number is how close the output is to the true clean signal, because it needs
no event matching and cannot be gamed by a tool that reports its work differently. Event
precision and recall come second, and are derived the same way for all three tools: a
sample the tool changed is a sample it claims was damaged. That is the only detection
signal Wave Corrector exposes, so everyone is read the same way.

Outputs are truncated to the shortest common length. Wave Corrector drops 11 samples off
the end of every file; nothing else differs in alignment.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train"))

from metrics import Score, hits, runs  # noqa: E402

MERGE_GAP = 22  # 0.5 ms, so one repair broken by a coincidentally unchanged sample stays one event


def snr_db(reference: np.ndarray, test: np.ndarray) -> float:
    error = float(((reference - test) ** 2).sum())
    if error == 0.0:
        return float("inf")
    return 10.0 * np.log10(float((reference**2).sum()) / error)


def merge(starts: np.ndarray, ends: np.ndarray, gap: int) -> tuple[np.ndarray, np.ndarray]:
    if starts.size == 0:
        return starts, ends
    keep = np.concatenate(([True], starts[1:] - ends[:-1] > gap))
    return starts[keep], ends[np.concatenate((keep[1:], [True]))]


def score_one(item: dict, corpus: Path, out: Path, name: str) -> dict | None:
    src = sf.read(str(corpus / f"{item['name']}.noisy.wav"), dtype="int16", always_2d=True)[0]
    truth = sf.read(str(corpus / f"{item['name']}.clean.wav"), dtype="int16", always_2d=True)[0]
    got = out / name / f"{item['name']}.wav"
    if not got.exists():
        return None
    dut = sf.read(str(got), dtype="int16", always_2d=True)[0]

    n = min(len(src), len(truth), len(dut))
    src, truth, dut = (a[:n].astype(np.float64) for a in (src, truth, dut))

    mask = np.unpackbits(np.load(corpus / f"{item['name']}.mask.npy"))
    mask = mask[: item["frames"] * 2].reshape(2, item["frames"])[:, :n].any(axis=0)

    changed = (dut != src).any(axis=1)
    pred = merge(*runs(changed), MERGE_GAP)
    true = runs(mask)

    row = {
        "name": item["name"], "set": item["set"], "tool": name,
        "snr_in": snr_db(truth, src), "snr_out": snr_db(truth, dut),
        "changed": int(changed.sum()), "frames": n,
        "change_dbfs": 10.0 * np.log10(max(((dut - src) ** 2).mean(), 1e-30) / 32768.0**2),
        "true_events": int(true[0].size), "pred_events": int(pred[0].size),
    }
    if item["set"] == "control":
        return row
    found = hits(true[0], true[1], pred[0], pred[1])
    row["tp"] = int(found.sum())
    row["fn"] = int((~found).sum())
    row["fp"] = int((~hits(pred[0], pred[1], true[0], true[1])).sum())
    # Energy the tool took out of samples that were never damaged: the music it ate.
    took = dut - src
    row["collateral_db"] = snr_db(src, np.where(mask[:, None], src, dut))
    row["took_off_target"] = float((took[~mask] ** 2).sum() / max((took**2).sum(), 1e-12))
    return row


def table(rows: list[dict], tools: list[str]) -> str:
    out = []
    for group in dict.fromkeys(r["set"] for r in rows):
        members = [r for r in rows if r["set"] == group]
        if not members:
            continue
        out.append(f"\n{group}  ({len({r['name'] for r in members})} files, "
                   f"{sum(r['frames'] for r in members if r['tool'] == tools[0]) / 44100:.0f} s)")
        if group == "control":
            out.append(f"  {'tool':<14}{'frames touched':>16}{'per minute':>13}"
                       f"{'damage dBFS':>14}{'worst file':>13}")
            for tool in tools:
                mine = [r for r in members if r["tool"] == tool]
                if not mine:
                    continue
                total = sum(r["changed"] for r in mine)
                seconds = sum(r["frames"] for r in mine) / 44100
                # Mean over files would be dominated by the quiet ones; pool the energy instead.
                pooled = 10.0 * np.log10(np.mean([10 ** (r["change_dbfs"] / 10) for r in mine]))
                worst = max(r["change_dbfs"] for r in mine)
                out.append(f"  {tool:<14}{total:>16,}{total / (seconds / 60):>13,.0f}"
                           f"{pooled:>14.1f}{worst:>13.1f}")
            continue
        base = [r for r in members if r["tool"] == tools[0]]
        out.append(f"  input SNR {np.mean([r['snr_in'] for r in base]):.1f} dB")
        out.append(f"  {'tool':<14}{'SNR out':>9}{'gain':>8}{'P':>8}{'R':>8}{'F1':>8}"
                   f"{'off-target':>12}")
        for tool in tools:
            mine = [r for r in members if r["tool"] == tool]
            if not mine:
                continue
            s = Score(tp=sum(r["tp"] for r in mine), fp=sum(r["fp"] for r in mine),
                      fn=sum(r["fn"] for r in mine))
            snr = np.mean([r["snr_out"] for r in mine])
            gain = snr - np.mean([r["snr_in"] for r in mine])
            off = np.mean([r["took_off_target"] for r in mine])
            out.append(f"  {tool:<14}{snr:>9.1f}{gain:>8.1f}{s.precision:>8.3f}"
                       f"{s.recall:>8.3f}{s.f1:>8.3f}{off:>11.1%}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", type=Path, default=Path("D:/tmp/bakeoff/corpus"))
    ap.add_argument("--out", type=Path, default=Path("D:/tmp/bakeoff/out"))
    ap.add_argument("--tools", nargs="+", default=["grooveclean", "nd", "wc"])
    a = ap.parse_args(argv)

    manifest = json.loads((a.corpus / "manifest.json").read_text(encoding="utf-8"))
    rows = [r for item in manifest for tool in a.tools
            if (r := score_one(item, a.corpus, a.out, tool)) is not None]
    (a.out / "scores.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(table(rows, a.tools))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
