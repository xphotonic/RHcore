#!/usr/bin/env python3
"""Verify file checksums recorded in an RO-Crate metadata file."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crate", required=True, help="Path to ro-crate-metadata.json")
    parser.add_argument("--root", default=".", help="Root directory for crate file paths")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    crate_path = Path(args.crate)
    root = Path(args.root)
    payload = json.loads(crate_path.read_text(encoding="utf-8"))
    graph = payload.get("@graph", [])
    if not isinstance(graph, list):
        raise ValueError("RO-Crate @graph must be a list")

    checked = 0
    for entry in graph:
        if not isinstance(entry, dict) or entry.get("@type") != "File":
            continue
        file_id = entry.get("@id")
        expected = entry.get("sha256") or entry.get("checksum")
        if not isinstance(file_id, str) or not isinstance(expected, str):
            continue
        expected = expected.removeprefix("sha256:")
        path = root / file_id
        if not path.exists():
            matches = list(root.rglob(Path(file_id).name))
            matching_hashes = [candidate for candidate in matches if sha256_file(candidate) == expected]
            if len(matching_hashes) == 1:
                path = matching_hashes[0]
            elif len(matching_hashes) > 1:
                raise FileNotFoundError(
                    f"RO-Crate file path is ambiguous after checksum matching: {file_id} -> {matching_hashes}"
                )
            elif not matches:
                raise FileNotFoundError(f"RO-Crate file is missing: {file_id}")
            else:
                raise ValueError(f"no candidate file matched recorded sha256 for {file_id}")
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError(f"sha256 mismatch for {file_id}: expected {expected}, got {actual}")
        checked += 1

    if checked == 0:
        raise ValueError("RO-Crate did not contain any verifiable File sha256/checksum entries")
    print(f"verified {checked} RO-Crate file checksum(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
