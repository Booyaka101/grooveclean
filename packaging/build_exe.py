"""Build dist/grooveclean-win64.exe against a CPU-only PyTorch.

The PyPI default torch wheel carries the CUDA runtime, which is about two gigabytes of DLLs
that a one-file exe would have to unpack on every run. The exe is for people without a GPU,
so it is built in a throwaway environment holding the CPU wheel instead.

    python packaging/build_exe.py

Pass --reuse to skip rebuilding that environment when iterating on the spec.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CPU_INDEX = "https://download.pytorch.org/whl/cpu"


def run(args: list[str]) -> None:
    print("$ " + " ".join(args), flush=True)
    subprocess.run(args, check=True, cwd=ROOT)


def make_env(env: Path, reuse: bool) -> Path:
    python = env / "Scripts" / "python.exe"
    if reuse and python.exists():
        # The project is copied into the environment, not linked, so reusing one still has to
        # refresh it or the exe ships whatever the source looked like the last time round.
        run([str(python), "-m", "pip", "install", "--no-deps", "--force-reinstall", str(ROOT)])
        return python
    shutil.rmtree(env, ignore_errors=True)
    run([sys.executable, "-m", "venv", str(env)])
    run([str(python), "-m", "pip", "install", "--upgrade", "pip", "wheel"])
    run([str(python), "-m", "pip", "install", "--index-url", CPU_INDEX, "torch"])
    run([str(python), "-m", "pip", "install", "pyinstaller>=6.10", str(ROOT)])
    return python


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--env", type=Path, default=ROOT / "build" / "exe-env")
    ap.add_argument("--reuse", action="store_true")
    args = ap.parse_args(argv)

    weights = ROOT / "src/grooveclean/weights/detector.pt"
    if not weights.exists():
        print(f"{weights}: train the detector before building the exe", file=sys.stderr)
        return 2

    python = make_env(args.env, args.reuse)
    run(
        [
            str(python), "-m", "PyInstaller", "--noconfirm", "--clean",
            "--distpath", str(ROOT / "dist"),
            "--workpath", str(ROOT / "build" / "pyinstaller"),
            str(ROOT / "packaging" / "grooveclean.spec"),
        ]
    )
    exe = ROOT / "dist" / "grooveclean-win64.exe"
    if not exe.exists():
        print("PyInstaller reported success but produced no exe", file=sys.stderr)
        return 1
    print(f"{exe} ({exe.stat().st_size / 2**20:.0f} MB)")
    run([str(exe), "--version"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
