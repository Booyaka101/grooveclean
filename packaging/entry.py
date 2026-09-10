"""PyInstaller entry point. Console scripts are not importable from a frozen bundle."""

import multiprocessing

from grooveclean.cli import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
