"""Exercise the installed CPU worker and bundled weights without a DAW."""

import os
import struct
import subprocess
import sys

import numpy as np
import torch

assert sys.version_info[:2] == (3, 11), 'Python 3.11 required'
assert struct.calcsize('P') == 8, '64-bit Python required'
assert torch.version.cuda is None, 'Install the CPU-only PyTorch build'
rate, channels = 44100, 2
audio = np.zeros((rate * 3, channels), dtype='<f4')
request = struct.pack('<4sIIIIff', b'GCRQ', 1, rate, channels, len(audio), 0.5, 20)
env = os.environ.copy()
env.pop('PYTHONPATH', None)
env['PYTHONNOUSERSITE'] = '1'
result = subprocess.run(
    [sys.executable, '-I', '-m', 'grooveclean.plugin_worker'],
    input=request + audio.tobytes(), capture_output=True, timeout=90, env=env,
)
if result.returncode:
    sys.stderr.buffer.write(result.stderr)
    raise RuntimeError(f'Worker exited with status {result.returncode}')
assert result.stdout[:8] == b'GCREADY1', 'Worker did not load bundled weights'
header = struct.unpack('<4sIII', result.stdout[8:24])
assert header == (b'GCRS', 1, 0, len(audio)), f'Invalid worker response: {header}'
assert len(result.stdout) == 24 + audio.nbytes, 'Wrong response length'
output = np.frombuffer(result.stdout[24:], dtype='<f4')
assert np.isfinite(output).all() and (output == 0).all(), 'Silence round-trip failed'
print(f'CPU worker and model passed: Python {sys.version.split()[0]}, torch {torch.__version__}')
