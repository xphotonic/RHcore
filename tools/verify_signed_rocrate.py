#!/usr/bin/env python3
"""Verify a signed RO-Crate tarball after Sigstore verification.

This script intentionally does not verify Sigstore itself. Run `cosign
verify-blob` first, then use this script to check the tarball checksum file,
extract the crate safely, and validate every File sha256 recorded in
ro-crate-metadata.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
import tempfile
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tar", required=True, help="RO-Crate tar.gz path")
    parser.add_argument("--sha256", default="", help="optional sha256sum sidecar")
    parser.add_argument("--expect-docker-digest", action="store_true")
    parser.add_argument("--expect-flint-commit", action="store_true")
    parser.add_argument("--expect-lean-tag", action="store_true")
    return parser.parse_args()


def assert_safe_member(member: tarfile.TarInfo) -> None:
    name = member.name
    if name.startswith("/") or ".." in Path(name).parts:
        raise ValueError(f"unsafe tar member path: {name}")


def verify_sidecar(tar_path: Path, sidecar_path: Path) -> None:
    if not sidecar_path:
        return
    expected = sidecar_path.read_text(encoding="utf-8").split()[0].removeprefix("sha256:")
    actual = sha256_file(tar_path)
    if actual != expected:
        raise ValueError(f"tarball sha256 mismatch: expected {expected}, got {actual}")


def file_entries(graph: list[dict]) -> list[dict]:
    return [
        entry for entry in graph
        if isinstance(entry, dict)
        and entry.get("@type") == "File"
        and isinstance(entry.get("@id"), str)
        and isinstance(entry.get("sha256") or entry.get("checksum"), str)
    ]


def collect_properties(graph: list[dict]) -> dict[str, str]:
    props: dict[str, str] = {}
    for entry in graph:
        if not isinstance(entry, dict):
            continue
        for prop in entry.get("additionalProperty", []):
            if isinstance(prop, dict) and "name" in prop and "value" in prop:
                props[str(prop["name"])] = str(prop["value"])
    return props


def main() -> int:
    args = parse_args()
    tar_path = Path(args.tar)
    sidecar_path = Path(args.sha256) if args.sha256 else None
    if sidecar_path:
        verify_sidecar(tar_path, sidecar_path)

    with tempfile.TemporaryDirectory(prefix="rocrate-verify-") as tmp:
        root = Path(tmp)
        with tarfile.open(tar_path, "r:gz") as tar:
            for member in tar.getmembers():
                assert_safe_member(member)
            tar.extractall(root)

        metadata_path = root / "ro-crate-metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError("missing ro-crate-metadata.json in RO-Crate")
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        graph = payload.get("@graph", [])
        if not isinstance(graph, list):
            raise ValueError("RO-Crate @graph must be a list")

        entries = file_entries(graph)
        if not entries:
            raise ValueError("RO-Crate has no File entries with sha256/checksum")
        for entry in entries:
            file_id = entry["@id"]
            expected = (entry.get("sha256") or entry.get("checksum")).removeprefix("sha256:")
            path = root / file_id
            if not path.exists():
                raise FileNotFoundError(f"missing crate file: {file_id}")
            actual = sha256_file(path)
            if actual != expected:
                raise ValueError(f"sha256 mismatch for {file_id}: expected {expected}, got {actual}")

        props = collect_properties(graph)
        required = {
            "docker:digest": args.expect_docker_digest,
            "flint:commit": args.expect_flint_commit,
            "lean:nightly": args.expect_lean_tag,
        }
        for key, enabled in required.items():
            if enabled and not props.get(key):
                raise ValueError(f"missing required RO-Crate property: {key}")

    print(f"verified signed RO-Crate payload: {tar_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

