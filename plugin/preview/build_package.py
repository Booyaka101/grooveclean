"""Assemble a reviewable test kit from an already-built VST3 and worker wheel."""

import argparse
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--wheel', type=Path, required=True)
    parser.add_argument('--sdk-license', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    if args.output.exists():
        raise SystemExit('Output already exists; choose a new directory.')
    with zipfile.ZipFile(args.wheel) as wheel:
        for path in sorted((root / 'src/grooveclean').rglob('*')):
            if not path.is_file() or path.suffix not in ('.py', '.pt', '.json'):
                continue
            name = path.relative_to(root / 'src').as_posix()
            if wheel.read(name) != path.read_bytes():
                raise SystemExit(f'Wheel differs from source: {name}')
    kit = args.output / 'GrooveClean-VST3-Windows-x64-preview'
    kit.mkdir(parents=True)
    scripts = ('Setup.ps1', 'Launch-DAW.ps1', 'Check-Worker.py', 'requirements.txt', 'README.txt')
    for name in scripts:
        shutil.copy2(Path(__file__).parent / name, kit / name)
    for name in ('LICENSE', 'CREDITS.md'):
        shutil.copy2(root / name, kit / name)
    (kit / 'worker').mkdir()
    shutil.copy2(args.wheel, kit / 'worker' / args.wheel.name)
    shutil.copytree(args.bundle, kit / 'GrooveClean.vst3')
    shutil.copy2(args.sdk_license, kit / 'VST3-SDK-LICENSE.txt')
    (kit / 'THIRD-PARTY.txt').write_text(
        'VST3 SDK: Steinberg Media Technologies GmbH, MIT license. See VST3-SDK-LICENSE.txt.\n'
        'Python dependencies are downloaded during setup under their respective licenses.\n'
        'PyTorch: https://github.com/pytorch/pytorch/blob/v2.6.0/LICENSE\n'
        'NumPy: https://github.com/numpy/numpy/blob/v2.2.6/LICENSE.txt\n'
        'SoundFile: https://github.com/bastibe/python-soundfile/blob/0.13.1/LICENSE\n'
        'Click: https://github.com/pallets/click/blob/8.1.8/LICENSE.rst\n', encoding='utf-8',
    )
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
    sources = sorted({name for name in tracked if name and (root / name).is_file()})
    # Include only project source, not recordings, CI credentials or local build products.
    sources = [name for name in sources if name.startswith(('src/', 'plugin/')) or
               name in ('LICENSE', 'CREDITS.md', 'README.md', 'CHANGELOG.md', 'pyproject.toml') or
               name.startswith('tests/test_plugin_')]
    with zipfile.ZipFile(kit / 'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources:
            archive.write(root / name, name)
    files = {p.relative_to(kit).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(kit.rglob('*')) if p.is_file()}
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode().strip()
    manifest = {
        'format': 1, 'kind': 'experimental-test-kit',
        'source_commit': commit,
        'source_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=root)),
        'files_sha256': files,
    }
    (kit / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    archive = Path(shutil.make_archive(str(kit), 'zip', args.output, kit.name))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.zip.sha256').write_text(f'{digest}  {archive.name}\n', encoding='ascii')
    print(archive)
    print(digest)


if __name__ == '__main__':
    main()
