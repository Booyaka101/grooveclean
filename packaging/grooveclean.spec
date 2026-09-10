# PyInstaller spec for the one-file Windows build. Driven by packaging/build_exe.py.
from pathlib import Path

from PyInstaller.utils.hooks import collect_dynamic_libs

ROOT = Path(SPECPATH).resolve().parent
WEIGHTS = ROOT / "src/grooveclean/weights/detector.pt"

analysis = Analysis(
    [str(ROOT / "packaging/entry.py")],
    pathex=[str(ROOT / "src")],
    binaries=collect_dynamic_libs("soundfile"),
    datas=[(str(WEIGHTS), "grooveclean/weights")],
    hiddenimports=["soundfile", "_soundfile_data"],
    # torchvision/torchaudio are not imported and pull in another few hundred MB if collected.
    excludes=["torchvision", "torchaudio", "matplotlib", "scipy", "pytest", "IPython", "tkinter"],
    noarchive=False,
)
pyz = PYZ(analysis.pure)
exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    name="grooveclean-win64",
    console=True,
    upx=False,
    strip=False,
)
