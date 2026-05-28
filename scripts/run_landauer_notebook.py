#!/usr/bin/env python3
"""Run notebooks/landauer.ipynb via Papermill with CLI arguments."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--trace-path", default="traces/run1.csv")
    p.add_argument("--block-size", type=int, default=5)
    p.add_argument("--cycle-column", default="cycle")
    p.add_argument("--typeb-json", default="inputs/typeB.json")
    p.add_argument("--sample-rate-hz", type=int, default=10000)
    p.add_argument("--bootstrap-reps", type=int, default=2000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--output-notebook", default="outputs/landauer.executed.ipynb")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    out_nb = Path(args.output_notebook)
    if not out_nb.is_absolute():
        out_nb = root / out_nb
    out_nb.parent.mkdir(parents=True, exist_ok=True)

    trace_path = Path(args.trace_path)
    if not trace_path.is_absolute():
        trace_path = root / trace_path
    typeb_json = Path(args.typeb_json)
    if not typeb_json.is_absolute():
        typeb_json = root / typeb_json
    if not trace_path.exists():
        raise SystemExit(f"missing trace file: {trace_path}")
    if not typeb_json.exists():
        raise SystemExit(f"missing type-B config: {typeb_json}")
    print(f"trace_path={trace_path}")
    print(f"typeb_json={typeb_json}")
    print(f"output_notebook={out_nb}")

    cmd = [
        sys.executable,
        "-m",
        "papermill",
        str(root / "notebooks/landauer.ipynb"),
        str(out_nb),
        "-p",
        "trace_path",
        str(trace_path),
        "-p",
        "block_size",
        str(args.block_size),
        "-p",
        "cycle_column",
        args.cycle_column,
        "-p",
        "typeb_json",
        str(typeb_json),
        "-p",
        "sample_rate_hz",
        str(args.sample_rate_hz),
        "-p",
        "bootstrap_reps",
        str(args.bootstrap_reps),
        "-p",
        "seed",
        str(args.seed),
    ]
    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
