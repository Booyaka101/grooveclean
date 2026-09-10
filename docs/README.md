# docs

Everything here is generated. Nothing is hand-drawn or typed in from memory.

| Script | Makes |
| --- | --- |
| `make_figure.py` | `before-after.png`, the README hero, from `tests/data/excerpt78.flac`. |
| `make_demo.py` | `demo/*.mp3`, ten seconds of `tests/data/demo78.flac`, before, after and the difference. |
| `make_screens.py` | A terminal shot of a command it actually runs, `--out` where you want it. |

`make_figure.py` needs matplotlib, `make_screens.py` needs Pillow, and `make_demo.py` needs a
libsndfile that can write MP3. None of them are dependencies of the package.

The demo uses a different side from the hero image. The figure wants the Sousa excerpt the
golden test is pinned to; the demo wants damage you can hear, which is a different thing.
`make_demo.py` brings the loudest of the three to -1 dBFS, so a quiet transfer is still
worth playing on laptop speakers. That one gain goes on all three, so before still equals
after plus removed.

Both excerpts are cut and their provenance recorded by `train/fetch_test_assets.py`, which
writes `tests/data/ASSETS.json`.

The two screenshots in the README were made with the sides in hand, not from anything in the
repo, so `make_screens.py` takes the command to run:

```
python docs/make_screens.py --out docs/shot-batch.png --cwd ~/transfers \
  -c "grooveclean batch sides -o cleaned --format flac"
```
