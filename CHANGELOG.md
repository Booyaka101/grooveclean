# Changelog

## 1.0.0 - 2026-09-10

First release.

- `grooveclean clean IN.wav -o OUT.wav` writes the cleaned audio, the exact difference file
  and a JSON report of every click.
- `grooveclean batch DIR -o OUTDIR` runs the same over a folder and keeps going past a file
  it cannot read.
- `--dry-run` on both commands writes the report only, for surveying a stack of transfers.
- `--skip-existing` on `batch` picks up where an interrupted run stopped.
- `--format` on `batch` chooses the output container. WAV, FLAC, AIFF, W64, CAF or RF64.
- Detection by a dilated 1-D CNN trained on real clicks harvested from 78rpm transfers,
  mixed into click-free netlabels music.
- Repair by least-squares autoregressive interpolation of order 64, batched so a whole side
  costs one solve per span width, with cubic fallback at the file edges.
- WAV, FLAC, AIFF, W64, CAF and RF64 input at 8 to 32 bit and 44.1 to 192 kHz, mono or
  stereo. Lossy input is refused with an explanation rather than processed.
- Streams in overlapping blocks, so file length is not bounded by memory.
- CUDA when it is there, CPU when it is not, `--device` to force either.
