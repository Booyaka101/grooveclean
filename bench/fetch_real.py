"""Fetch minutes of real 78 transfers for the no-ground-truth half of the bake-off.

The checked-in test excerpts are 20 seconds total, which separated nothing. These are whole
sides from the held-out split of the same archive.org collection the click bank was harvested
from, so no tool has seen them and the damage is real rather than mixed in.

Audio is kept at the source rate: resampling would hand every tool a different high band from
the one its own defaults were tuned against.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train"))

import _ia  # noqa: E402

LEAD_IN_S = 15.0  # the run-in groove is noise with no music under it, and would flatter everyone
FLAC_BYTES_PER_S = 4.5  # per Hz of sample rate, stereo 24-bit worst case with margin


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=Path("D:/tmp/bakeoff/real"))
    ap.add_argument("--manifest", type=Path, default=ROOT / "corpus/noise/manifest.json")
    ap.add_argument("--items", type=int, default=12)
    ap.add_argument("--seconds", type=float, default=45.0)
    ap.add_argument("--stride", type=int, default=1, help="Every Nth item, for parallel runs.")
    ap.add_argument("--offset", type=int, default=0)
    a = ap.parse_args(argv)

    pool = [i for i in json.loads(a.manifest.read_text(encoding="utf-8"))["items"]
            if i["split"] == "test"][a.offset::a.stride]
    print(f"{len(pool)} test-split items to draw from")
    a.out.mkdir(parents=True, exist_ok=True)
    work = a.out / "work"
    got = []
    for item in pool:
        if len(got) >= a.items:
            break
        rate = int(item["rate"])
        want = int((LEAD_IN_S + a.seconds) * rate)
        head = int(want * FLAC_BYTES_PER_S)
        try:
            audio, _ = _ia.fetch_audio(
                item["identifier"], work,
                whole_below=head, head_bytes=head, rate_out=rate)
        except Exception as exc:  # noqa: BLE001 - archive.org fails in many ways, all skippable
            print(f"  skip {item['identifier'][:60]}: {exc}")
            continue
        if audio.shape[0] < want:
            print(f"  skip {item['identifier'][:60]}: only {audio.shape[0] / rate:.0f}s")
            continue
        cut = audio[int(LEAD_IN_S * rate):want]
        path = a.out / f"{item['identifier'][:60]}.wav"
        sf.write(str(path), cut, rate, subtype="PCM_16")
        got.append(path)
        print(f"  {path.name}: {cut.shape[0] / rate:.0f}s, {rate} Hz, {cut.shape[1]}ch")
    print(f"\n{len(got)} sides, {len(got) * a.seconds / 60:.1f} minutes -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
