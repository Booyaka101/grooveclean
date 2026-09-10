"""Shared Internet Archive access for the two harvesters.

Both corpora come from the same place and differ only in what gets extracted from the audio,
so search, metadata, the polite retrying downloader and the train/test split live here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterable, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from grooveclean import detect  # noqa: E402

SEARCH_URL = "https://archive.org/advancedsearch.php"
METADATA_URL = "https://archive.org/metadata/"
DOWNLOAD_URL = "https://archive.org/download/"
USER_AGENT = "grooveclean-harvester/1.0 (+https://github.com/Booyaka101/grooveclean)"

TEST_SPLIT_IN_TEN = 1  # one identifier in ten is held out, by hash of the identifier


class HarvestError(Exception):
    pass


def _get(url: str, timeout: float = 60.0, retries: int = 4) -> bytes:
    last: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in (429, 503, 502, 504):
                time.sleep(2.0 * (attempt + 1))
                continue
            raise HarvestError(f"{url}: HTTP {exc.code} {exc.reason}") from exc
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last = exc
            time.sleep(2.0 * (attempt + 1))
    raise HarvestError(f"{url}: giving up after {retries} attempts ({last})")


def search(query: str, rows: int, fields: Sequence[str]) -> list[dict]:
    """One advancedsearch page. Archive.org caps a single page well below numFound."""
    params = [("q", query), ("rows", str(rows)), ("output", "json"), ("start", "0")]
    params += [("fl[]", f) for f in fields]
    body = _get(f"{SEARCH_URL}?{urllib.parse.urlencode(params)}", timeout=120.0)
    try:
        payload = json.loads(body)["response"]
    except (ValueError, KeyError) as exc:
        raise HarvestError(f"unexpected search response for {query!r}: {body[:200]!r}") from exc
    return payload["docs"]


def metadata(identifier: str) -> dict:
    return json.loads(_get(f"{METADATA_URL}{urllib.parse.quote(identifier)}"))


def flac_files(meta: dict) -> list[dict]:
    """FLAC entries only. Items whose sole audio is VBR MP3 are skipped, never transcoded."""
    out = []
    for f in meta.get("files", []):
        # The collection labels lossless files both "Flac" and "24bit Flac".
        name = f.get("name", "").lower()
        if "flac" in str(f.get("format", "")).lower() and name.endswith(".flac"):
            out.append({"name": f["name"], "size": int(f.get("size") or 0)})
    return sorted(out, key=lambda f: f["name"])


def download(
    identifier: str, name: str, dest: Path, timeout: float = 60.0, max_bytes: int | None = None
) -> Path:
    """Fetch a file, optionally only its first `max_bytes`.

    A 78 side's lead-in groove is at the front of the file, so a partial fetch is usually all
    the harvester needs; FLAC decodes happily up to wherever the bytes stop.

    ``timeout`` is per socket read, so it bounds a stall rather than the whole transfer. Keep
    it short: archive.org hands out plenty of connections that open and then never deliver,
    and there is always another item.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = DOWNLOAD_URL + urllib.parse.quote(identifier) + "/" + urllib.parse.quote(name)
    headers = {"User-Agent": USER_AGENT}
    if max_bytes:
        headers["Range"] = f"bytes=0-{max_bytes - 1}"
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp, tmp.open("wb") as fh:
        written = 0
        while chunk := resp.read(1 << 20):
            fh.write(chunk)
            written += len(chunk)
            if max_bytes and written >= max_bytes:
                break
    tmp.replace(dest)
    return dest


def fetch_audio(
    identifier: str,
    work_dir: Path,
    *,
    whole_below: int,
    head_bytes: int,
    rate_out: int,
) -> tuple[np.ndarray, dict]:
    """Download the item's smallest FLAC and decode it to `rate_out`, as [frames, channels].

    Large transfers are range-fetched, so the decode stops mid-frame; that is expected and the
    partial audio is kept rather than discarded.
    """
    files = [f for f in flac_files(metadata(identifier)) if f["size"] > 0]
    if not files:
        raise HarvestError("no FLAC in item")
    pick = min(files, key=lambda f: f["size"])
    head = None if pick["size"] <= whole_below else head_bytes
    work_dir.mkdir(parents=True, exist_ok=True)
    path = work_dir / f"{identifier}.flac"
    try:
        download(identifier, pick["name"], path, max_bytes=head)
        chunks = []
        with sf.SoundFile(str(path)) as fh:
            rate = fh.samplerate
            try:
                while len(block := fh.read(1 << 18, dtype="float32", always_2d=True)):
                    chunks.append(block)
            except sf.LibsndfileError:
                pass
        if not chunks:
            raise HarvestError("no decodable audio")
        data = np.concatenate(chunks)
    finally:
        path.unlink(missing_ok=True)
    if rate != rate_out:
        n_out = int(round(data.shape[0] * rate_out / rate))
        data = detect.resample(torch.from_numpy(data.T.copy()), n_out).numpy().T
    info = {"file": pick["name"], "bytes": head or pick["size"], "rate": rate}
    return np.ascontiguousarray(data), info


def build_parser(description: str, items: int, out: str) -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--items", type=int, default=items)
    ap.add_argument("--out", type=Path, default=Path(out))
    ap.add_argument("--work", type=Path, default=Path("corpus/.work"))
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--seed", type=int, default=20260910)
    return ap


def seed_of(identifier: str) -> int:
    """Stable per-item RNG seed, so a re-harvest of the same item reproduces the same picks."""
    return int.from_bytes(hashlib.sha1(identifier.encode("utf-8")).digest()[:4], "big")


def split_of(identifier: str) -> str:
    """Deterministic per-identifier split so no source item ever lands in both halves."""
    digest = hashlib.sha1(identifier.encode("utf-8")).digest()
    return "test" if digest[0] % 10 < TEST_SPLIT_IN_TEN else "train"


def sample_identifiers(docs: Iterable[dict], count: int, seed: int) -> list[dict]:
    docs = sorted(docs, key=lambda d: d["identifier"])
    random.Random(seed).shuffle(docs)
    return docs[:count]


@dataclass(slots=True)
class Outcome:
    identifier: str
    status: str  # "ok" | "skip" | "error"
    detail: str = ""
    payload: dict | None = None


@dataclass(frozen=True, slots=True)
class Collection:
    """What separates one harvester from the other: which archive.org items it wants."""

    query: str
    rows: int
    fields: Sequence[str]
    label: str
    banner: str


def harvest(
    collection: Collection, args: argparse.Namespace, worker: Callable[[dict], Outcome]
) -> int:
    """Search, sample, run the worker over the sample, write the manifest."""
    args.out.mkdir(parents=True, exist_ok=True)
    args.work.mkdir(parents=True, exist_ok=True)
    try:
        docs = search(collection.query, collection.rows, collection.fields)
    except HarvestError as exc:
        print(f"archive.org search failed: {exc}", file=sys.stderr)
        return 2
    picked = sample_identifiers(docs, args.items, args.seed)
    print(f"{collection.banner}: {len(docs)} in page, harvesting {len(picked)}", flush=True)
    run_pool(picked, worker, args.workers, args.out / "manifest.json", collection.label)
    return 0


def run_cli(entry: Callable[[], int]) -> int:
    """Exit code for a harvester's __main__. Ctrl-C is a line, not a traceback."""
    try:
        return entry()
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


def run_pool(
    items: Sequence[dict],
    worker: Callable[[dict], Outcome],
    workers: int,
    manifest_path: Path,
    label: str,
) -> list[Outcome]:
    """Run `worker` over `items`, printing one line per item and writing a provenance manifest."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    results: list[Outcome] = []
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        # as_completed, not map: one slow download would otherwise hold back every line
        # behind it and the run would look hung for minutes at a time.
        futures = [pool.submit(worker, item) for item in items]
        for future in as_completed(futures):
            outcome = future.result()
            done += 1
            results.append(outcome)
            print(
                f"[{label} {done}/{len(items)}] {outcome.status:<5} {outcome.identifier} "
                f"{outcome.detail}",
                flush=True,
            )
    kept = [r for r in results if r.status == "ok"]
    items = read_manifest(manifest_path, label)
    for r in kept:
        items[r.identifier] = {
            "identifier": r.identifier,
            "split": split_of(r.identifier),
            **(r.payload or {}),
        }
    manifest_path.write_text(
        json.dumps({"source": label, "items": [items[k] for k in sorted(items)]}, indent=2),
        encoding="utf-8",
    )
    print(
        f"{label}: {len(kept)} kept, {len(results) - len(kept)} skipped/failed, "
        f"{len(items)} in the manifest",
        flush=True,
    )
    return results


def read_manifest(path: Path, label: str) -> dict[str, dict]:
    """Existing provenance by identifier, so a second harvest adds to it instead of replacing it."""
    if not path.exists():
        return {}
    blob = json.loads(path.read_text(encoding="utf-8"))
    if blob.get("source") != label:
        return {}
    return {item["identifier"]: item for item in blob["items"]}
