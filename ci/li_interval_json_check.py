#!/usr/bin/env python3
"""Card 2: numeric positivity check from li_intervals.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intervals", required=True)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--out", default="artifacts/li_positivity.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    src = Path(args.intervals)
    data = json.loads(src.read_text(encoding="utf-8"))
    rows = data.get("intervals", [])
    sample = rows[: args.limit]

    if len(sample) < args.limit:
        result = {
            "card": "li-positivity-lean",
            "status": "FAIL",
            "error": f"expected at least {args.limit} intervals, got {len(sample)}",
        }
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return 1

    failing = []
    for row in sample:
        lo = float(row["lo"])
        hi = float(row["hi"])
        n = int(row["n"])
        if not (lo > 0.0 and lo <= hi):
            failing.append({"n": n, "lo": lo, "hi": hi})

    status = "PASS" if not failing else "FAIL"
    result = {
        "card": "li-positivity-lean",
        "limit": args.limit,
        "checked": len(sample),
        "failing": failing,
        "status": status,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

