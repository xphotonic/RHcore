#!/usr/bin/env python3
"""
Zenodo intake helper.

Downloads dataset files from Zenodo records and feeds them through
tools/zenodo_adapter.py to produce normalized trace + provenance artifacts.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen, urlretrieve

DATASET_CHOICES = ("szilard", "ot_arhmm", "cantilever")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", choices=DATASET_CHOICES, help="Dataset key.")
    p.add_argument("--record-url", help="Zenodo record URL, e.g. https://zenodo.org/records/14516010")
    p.add_argument("--doi", help="DOI fallback, e.g. 10.5281/zenodo.14516010")
    p.add_argument("--license", default="", help="License override (e.g., CC-BY-4.0)")
    p.add_argument("--sources-json", default="repo/data/experimental/zenodo_sources.json")
    p.add_argument("--all", action="store_true", help="Process every source from --sources-json.")
    p.add_argument("--download-dir", default="repo/data/experimental/raw")
    p.add_argument("--out-dir", default="repo/data/experimental")
    p.add_argument("--strict-landauer", action="store_true")
    return p.parse_args()


def _read_json(url: str) -> dict:
    with urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _record_id_from_url(record_url: str) -> str:
    m = re.search(r"/records/(\d+)", record_url)
    if not m:
        raise ValueError(f"could not parse record id from URL: {record_url}")
    return m.group(1)


def _resolve_record_from_doi(doi: str) -> dict:
    q = f'https://zenodo.org/api/records?q=doi:"{doi}"&size=1&sort=mostrecent'
    payload = _read_json(q)
    hits = payload.get("hits", {}).get("hits", [])
    if not hits:
        raise ValueError(f"no Zenodo records found for DOI {doi}")
    return hits[0]


def _fetch_record(record_url: str | None, doi: str | None) -> tuple[dict, str]:
    if record_url:
        record_id = _record_id_from_url(record_url)
        return _read_json(f"https://zenodo.org/api/records/{record_id}"), record_url
    if doi:
        rec = _resolve_record_from_doi(doi)
        rid = str(rec.get("id", ""))
        resolved_url = f"https://zenodo.org/records/{rid}" if rid else ""
        return rec, resolved_url
    raise ValueError("provide either --record-url or --doi")


def _pick_file(record: dict) -> dict:
    files = record.get("files", [])
    if not files:
        raise ValueError("record has no downloadable files")

    def score(f: dict) -> tuple[int, int]:
        key = str(f.get("key", "")).lower()
        size = int(f.get("size", 0))
        if key.endswith(".zip"):
            priority = 3
        elif key.endswith(".csv"):
            priority = 2
        elif key.endswith(".mat"):
            priority = 1
        else:
            priority = 0
        return (priority, size)

    files = sorted(files, key=score, reverse=True)
    chosen = files[0]
    if score(chosen)[0] == 0:
        raise ValueError("no zip/csv/mat files found in record")
    return chosen


def _download_file(file_entry: dict, download_dir: Path) -> Path:
    download_dir.mkdir(parents=True, exist_ok=True)
    key = file_entry.get("key", "download.bin")
    url = file_entry.get("links", {}).get("self")
    if not url:
        raise ValueError(f"missing file URL for {key}")
    out = download_dir / Path(key).name
    urlretrieve(url, out)
    return out


def _run_adapter(
    dataset: str,
    input_path: Path,
    out_dir: Path,
    doi: str,
    license_id: str,
    record_url: str,
    strict_landauer: bool,
) -> int:
    cmd = [
        sys.executable,
        "tools/zenodo_adapter.py",
        "--dataset",
        dataset,
        "--input",
        str(input_path),
        "--out-dir",
        str(out_dir),
        "--doi",
        doi,
        "--license",
        license_id,
        "--record-url",
        record_url,
    ]
    if strict_landauer:
        cmd.append("--strict-landauer")
    return subprocess.run(cmd, check=False).returncode


def _process_one(
    dataset: str,
    record_url: str | None,
    doi: str | None,
    license_override: str,
    download_dir: Path,
    out_dir: Path,
    strict_landauer: bool,
) -> int:
    record, resolved_url = _fetch_record(record_url, doi)
    chosen = _pick_file(record)
    local_file = _download_file(chosen, download_dir)

    metadata = record.get("metadata", {})
    resolved_doi = metadata.get("doi", doi or "")
    license_meta = metadata.get("license", {})
    resolved_license = (
        license_override
        or license_meta.get("id")
        or metadata.get("access_right")
        or ""
    )

    print(
        json.dumps(
            {
                "dataset": dataset,
                "record_url": resolved_url,
                "downloaded_file": str(local_file),
                "doi": resolved_doi,
                "license": resolved_license,
            },
            indent=2,
        )
    )

    return _run_adapter(
        dataset=dataset,
        input_path=local_file,
        out_dir=out_dir,
        doi=resolved_doi,
        license_id=resolved_license,
        record_url=resolved_url,
        strict_landauer=strict_landauer,
    )


def _run_all(args: argparse.Namespace) -> int:
    sources_path = Path(args.sources_json)
    if not sources_path.exists():
        raise FileNotFoundError(f"sources json not found: {sources_path}")
    sources = json.loads(sources_path.read_text(encoding="utf-8"))
    if not isinstance(sources, list):
        raise ValueError("sources json must be a JSON array")

    rc = 0
    for src in sources:
        dataset = src.get("dataset", "")
        if dataset not in DATASET_CHOICES:
            print(f"skip invalid dataset entry: {dataset}", file=sys.stderr)
            rc = 1
            continue
        one_rc = _process_one(
            dataset=dataset,
            record_url=src.get("record_url"),
            doi=src.get("doi"),
            license_override=src.get("license", ""),
            download_dir=Path(args.download_dir),
            out_dir=Path(args.out_dir),
            strict_landauer=args.strict_landauer,
        )
        if one_rc != 0:
            rc = one_rc
    return rc


def main() -> int:
    args = parse_args()
    if args.all:
        return _run_all(args)

    if not args.dataset:
        print("error: --dataset is required unless --all is set", file=sys.stderr)
        return 1
    if not args.record_url and not args.doi:
        print("error: provide --record-url or --doi", file=sys.stderr)
        return 1

    return _process_one(
        dataset=args.dataset,
        record_url=args.record_url,
        doi=args.doi,
        license_override=args.license,
        download_dir=Path(args.download_dir),
        out_dir=Path(args.out_dir),
        strict_landauer=args.strict_landauer,
    )


if __name__ == "__main__":
    raise SystemExit(main())
