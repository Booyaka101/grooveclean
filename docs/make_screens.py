"""Render a terminal shot of a real command run.

Runs each --command for real, captures what it printed, and draws it. Nothing is typed in
by hand, so the picture cannot drift away from what the tool does.

    python docs/make_screens.py --out docs/shot.png --cwd . -c "grooveclean clean -h"

Needs Pillow:

    pip install pillow
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SCALE = 2
FONT_SIZE = 13 * SCALE
LINE_GAP = 6 * SCALE
PAD = 26 * SCALE
RADIUS = 10 * SCALE

BACKGROUND = "#16181d"
PROMPT = "#eb6834"
COMMAND = "#f4f4f1"
OUTPUT = "#b4b8c0"

FONTS = (
    "C:/Windows/Fonts/CascadiaMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/System/Library/Fonts/Menlo.ttc",
)


def load_font() -> ImageFont.FreeTypeFont:
    for candidate in FONTS:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, FONT_SIZE)
    import matplotlib

    bundled = Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSansMono.ttf"
    return ImageFont.truetype(str(bundled), FONT_SIZE)


def transcript(commands: list[str], cwd: Path, prompt: str) -> list[tuple[str, str]]:
    """Run each command and return (colour, text) lines, the prompt line then its output."""
    lines: list[tuple[str, str]] = []
    for command in commands:
        lines.append(("prompt", f"{prompt} {command}"))
        done = subprocess.run(
            shlex.split(command),
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        body = (done.stderr + done.stdout).replace("\r", "").rstrip("\n")
        if body:
            lines.extend(("output", line) for line in body.split("\n"))
        lines.append(("blank", ""))
    while lines and lines[-1][1] == "":
        lines.pop()
    return lines


def render(lines: list[tuple[str, str]], font: ImageFont.FreeTypeFont) -> Image.Image:
    step = font.getbbox("Ay")[3] + LINE_GAP
    ruler = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    width = max((ruler.textlength(text, font=font) for _, text in lines), default=0)
    size = (int(width) + PAD * 2, step * len(lines) + PAD * 2 - LINE_GAP)

    image = Image.new("RGB", size, BACKGROUND)
    draw = ImageDraw.Draw(image)
    for index, (kind, text) in enumerate(lines):
        y = PAD + index * step
        if kind == "prompt":
            head, rest = text.split(" ", 1)
            draw.text((PAD, y), head, font=font, fill=PROMPT)
            draw.text((PAD + ruler.textlength(head + " ", font=font), y), rest, font=font,
                      fill=COMMAND)
        elif kind == "output":
            draw.text((PAD, y), text, font=font, fill=OUTPUT)
    return round_corners(image)


def round_corners(image: Image.Image) -> Image.Image:
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *[n - 1 for n in image.size]), RADIUS, fill=255)
    out = Image.new("RGBA", image.size, (0, 0, 0, 0))
    out.paste(image, mask=mask)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--cwd", type=Path, default=Path.cwd())
    ap.add_argument("--prompt", default="$")
    ap.add_argument("-c", "--command", action="append", required=True)
    args = ap.parse_args(argv)

    lines = transcript(args.command, args.cwd, args.prompt)
    if not lines:
        print("nothing to draw", file=sys.stderr)
        return 1
    image = render(lines, load_font())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.out)
    print(f"wrote {args.out} ({image.width}x{image.height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
