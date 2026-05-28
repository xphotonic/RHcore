#!/usr/bin/env python3
"""L0 sanity checks for a prechecked zeta zero table."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run L0 zero-table sanity checks.")
    parser.add_argument("--zeros", required=True, help="Path to the zero table CSV.")
    return parser.parse_args()


def detect_t_column(fieldnames: list[str]) -> str:
    lowered = {name.lower(): name for name in fieldnames}
    for candidate in ("t", "imag", "imaginary", "ordinate", "zero"):
        if candidate in lowered:
            return lowered[candidate]
    return fieldnames[0]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    zeros_path = Path(args.zeros)

    result: dict[str, object] = {
        "layer": "zeros",
        "status": "FAIL",
        "representation": "ordered_ordinates_with_checksum",
        "source": str(zeros_path),
    }

    if not zeros_path.exists():
        result["error"] = "zeros file does not exist"
        print(json.dumps(result, indent=2))
        return 1

    try:
        with zeros_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise ValueError("missing CSV header")
            t_column = detect_t_column(list(reader.fieldnames))
            ordinates = []
            for row_index, row in enumerate(reader, start=2):
                raw_value = row.get(t_column, "")
                value = float(raw_value)
                if not math.isfinite(value):
                    raise ValueError(f"non-finite ordinate on row {row_index}")
                ordinates.append(value)
    except Exception as exc:  # pragma: no cover - surfaced in artifact
        result["error"] = str(exc)
        print(json.dumps(result, indent=2))
        return 1

    if not ordinates:
        result["error"] = "no ordinates found"
        print(json.dumps(result, indent=2))
        return 1

    monotonic = all(left < right for left, right in zip(ordinates, ordinates[1:]))
    positive = all(value > 0.0 for value in ordinates)
    finite = all(math.isfinite(value) for value in ordinates)

    result.update(
        {
            "status": "PASS" if monotonic and positive and finite else "FAIL",
            "checks": {
                "count": len(ordinates),
                "monotonic_increasing": monotonic,
                "strictly_positive": positive,
                "finite": finite,
            },
            "summary": {
                "min_t": min(ordinates),
                "max_t": max(ordinates),
                "zeros_checksum": sha256_file(zeros_path),
                "sha256": sha256_file(zeros_path),
                "t_column": t_column,
            },
        }
    )

    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
