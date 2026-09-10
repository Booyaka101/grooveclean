"""Turn the harvest manifests into CREDITS.md.

Every item that contributed to the shipped detector is listed with its archive.org identifier
and which side of the train/test split it fell on.

    python train/make_credits.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DETAILS = "https://archive.org/details/"


def load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path}: no manifest; run the harvester first")
    return json.loads(path.read_text(encoding="utf-8"))["items"]


def describe(item: dict) -> str:
    title = (item.get("title") or item["identifier"]).strip()
    creator = item.get("creator")
    if isinstance(creator, list):
        creator = ", ".join(creator)
    label = f"{title} - {creator}" if creator else title
    return label.replace("|", "/").replace("\n", " ")[:110]


def table(items: list[dict], extra: str, unit: str) -> list[str]:
    rows = [f"| Item | {unit} | Split |", "| --- | --- | --- |"]
    for item in sorted(items, key=lambda i: i["identifier"]):
        link = f"[{describe(item)}]({DETAILS}{item['identifier']})"
        rows.append(f"| {link} | {item.get(extra, '')} | {item['split']} |")
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    ap.add_argument("--noise", type=Path, default=root / "corpus/noise/manifest.json")
    ap.add_argument("--clean", type=Path, default=root / "corpus/clean/manifest.json")
    ap.add_argument("--out", type=Path, default=root / "CREDITS.md")
    args = ap.parse_args(argv)

    noise, clean = load(args.noise), load(args.clean)
    total_clicks = sum(int(item.get("clicks", 0)) for item in noise)
    lines = [
        "# Credits",
        "",
        "The detector shipped in `src/grooveclean/weights/detector.pt` was trained on audio from",
        "the Internet Archive. Clicks came from the [78rpm](https://archive.org/details/78rpm)",
        "collection, whose transfers are of recordings in the public domain in the United States.",
        "Clean music came from the [netlabels](https://archive.org/details/netlabels) collection,",
        "released by its artists under Creative Commons and similar licences.",
        "",
        "What ships is mostly a set of network weights. The audio that is checked in is",
        "`tests/data/excerpt78.flac`, `tests/data/clean_excerpt.flac` and",
        "`tests/data/demo78.flac`, all three credited in `tests/data/ASSETS.json`, and",
        "`tests/data/detector_eval.flac`, whose music is drawn only from the public domain",
        "and CC-BY items in the table below.",
        "",
        "`demo78.flac` is the side you hear in `docs/demo/`. It was not used for training or for",
        "scoring, so it appears in neither table.",
        "",
        "Items marked `test` were held out of training and used only to score the detector.",
        "",
        f"## Clicks: {len(noise)} 78rpm transfers, {total_clicks:,} click waveforms",
        "",
        *table(noise, "clicks", "Clicks"),
        "",
        f"## Clean music: {len(clean)} netlabels releases",
        "",
        *table(clean, "licenseurl", "Licence"),
        "",
    ]
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.out} ({len(noise) + len(clean)} items)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
