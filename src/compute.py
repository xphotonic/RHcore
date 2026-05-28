#!/usr/bin/env python3
"""Deterministic numeric stub + run manifest emitter for reproducible compute."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import random
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_zero_table(n: int, seed: int) -> list[tuple[int, float]]:
    random.seed(seed)
    rows: list[tuple[int, float]] = []
    for i in range(n):
        value = (i + 1) * 0.123456789 + random.uniform(-1e-12, 1e-12)
        rows.append((i, value))
    return rows


def write_zero_table(path: Path, rows: list[tuple[int, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["index", "value"])
        writer.writerows(rows)


def git_commit() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True)
            .strip()
        )
    except Exception:
        return os.environ.get("GITHUB_SHA", "unknown")


@dataclass
class ManifestConfig:
    run_id: str
    lock_file: Path
    input_s3: str
    input_sha256: str
    instance_type: str
    is_spot: bool


def build_manifest(cfg: ManifestConfig) -> dict[str, Any]:
    lock_sha = file_sha256(cfg.lock_file) if cfg.lock_file.exists() else None
    return {
        "run_id": cfg.run_id,
        "time_utc": utc_now_iso(),
        "git_commit": git_commit(),
        "platform": {
            "python": platform.python_version(),
            "system": platform.platform(),
        },
        "environment": {
            "lock_file": str(cfg.lock_file),
            "lock_sha256": lock_sha,
        },
        "inputs": [
            {
                "s3": cfg.input_s3,
                "sha256": cfg.input_sha256,
            }
        ],
        "instance": {
            "type": cfg.instance_type,
            "spot": cfg.is_spot,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", help="Path for ZERO_TABLE.csv")
    parser.add_argument("--n", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--manifest", help="Path for RH_STATE.json")
    parser.add_argument("--emit-manifest", action="store_true")
    parser.add_argument("--run-id", default="local")
    parser.add_argument("--lock-file", default="env.lock")
    parser.add_argument("--input-s3", default="s3://data/zeros/v1")
    parser.add_argument("--input-sha256", default="unknown")
    parser.add_argument("--instance-type", default="ml.t3.medium")
    parser.add_argument("--spot", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.out:
        rows = compute_zero_table(args.n, args.seed)
        write_zero_table(Path(args.out), rows)

    if args.emit_manifest and args.manifest:
        manifest = build_manifest(
            ManifestConfig(
                run_id=args.run_id,
                lock_file=Path(args.lock_file),
                input_s3=args.input_s3,
                input_sha256=args.input_sha256,
                instance_type=args.instance_type,
                is_spot=bool(args.spot),
            )
        )
        manifest_path = Path(args.manifest)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

