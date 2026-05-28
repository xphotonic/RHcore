#!/usr/bin/env python3
"""Create and append L2/Li session tracker CSV rows.

Missing numeric fields are written as the literal UNDEFINED so downstream
trackers do not silently parse blanks as zero or null.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path


HEADER = [
    "session_id",
    "date_utc",
    "lambda",
    "theta_prime",
    "ratio",
    "spectral_concentration",
    "STATE",
    "GAP",
    "STATUS",
    "NEXT",
    "notes",
]

NUMERIC_FIELDS = {"lambda", "theta_prime", "ratio", "spectral_concentration"}
STATUS_VALUES = {"PASS", "FAIL", "WARN", "UNDEFINED"}
UNDEFINED = "UNDEFINED"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="l2_sessions.csv", help="CSV path to create or append")
    parser.add_argument("--init-only", action="store_true", help="write only the header if the file is missing")
    parser.add_argument("--session-id", default="", help="session identifier, e.g. S001")
    parser.add_argument("--date-utc", default="", help="ISO UTC timestamp; defaults to current UTC")
    parser.add_argument("--lambda", dest="lambda_", default=UNDEFINED)
    parser.add_argument("--theta-prime", default=UNDEFINED)
    parser.add_argument("--ratio", default=UNDEFINED)
    parser.add_argument("--spectral-concentration", default=UNDEFINED)
    parser.add_argument("--state", default=UNDEFINED)
    parser.add_argument("--gap", default=UNDEFINED)
    parser.add_argument("--status", default=UNDEFINED, choices=sorted(STATUS_VALUES))
    parser.add_argument("--next", default=UNDEFINED, help="next action")
    parser.add_argument("--notes", default=UNDEFINED)
    return parser.parse_args()


def normalize(value: str | None) -> str:
    if value is None:
        return UNDEFINED
    text = str(value).strip()
    return text if text else UNDEFINED


def validate_numeric(name: str, value: str) -> None:
    if value == UNDEFINED:
        return
    try:
        Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{name} must be numeric or UNDEFINED, got {value!r}") from exc


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_header(path: Path) -> None:
    if path.exists() and path.stat().st_size > 0:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            current = next(reader, None)
        if current != HEADER:
            raise ValueError(f"{path} has unexpected header: {current!r}")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerow(HEADER)


def build_row(args: argparse.Namespace) -> list[str]:
    row = {
        "session_id": normalize(args.session_id),
        "date_utc": normalize(args.date_utc) if args.date_utc else utc_now(),
        "lambda": normalize(args.lambda_),
        "theta_prime": normalize(args.theta_prime),
        "ratio": normalize(args.ratio),
        "spectral_concentration": normalize(args.spectral_concentration),
        "STATE": normalize(args.state),
        "GAP": normalize(args.gap),
        "STATUS": normalize(args.status),
        "NEXT": normalize(args.next),
        "notes": normalize(args.notes),
    }
    for name in NUMERIC_FIELDS:
        validate_numeric(name, row[name])
    return [row[name] for name in HEADER]


def main() -> int:
    args = parse_args()
    out_path = Path(args.out)
    ensure_header(out_path)
    if args.init_only:
        print(out_path)
        return 0

    row = build_row(args)
    with out_path.open("a", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerow(row)
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

