#!/usr/bin/env python3
"""Emit RH_STATE.json — the run manifest for reproducibility and attestation."""

from __future__ import annotations
import argparse, hashlib, json, os, platform, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--run-id",         required=True)
    p.add_argument("--zeros",          required=True)
    p.add_argument("--closure-status", required=True)
    p.add_argument("--out",            required=True)
    return p.parse_args()


def sha256(path: Path) -> str:
    d = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            d.update(chunk)
    return d.hexdigest()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return os.environ.get("GITHUB_SHA", "unknown")


def python_version() -> str:
    return platform.python_version()


def requirements_hash() -> str:
    req = Path("requirements.txt")
    return sha256(req) if req.exists() else "missing"


def main() -> int:
    args          = parse_args()
    zeros_path    = Path(args.zeros)
    closure_path  = Path(args.closure_status)
    out_path      = Path(args.out)

    closure_status = "unknown"
    if closure_path.exists():
        try:
            closure_status = json.loads(closure_path.read_text())["status"]
        except Exception:
            pass

    state = {
        "schema":          "rh_state/v1",
        "run_id":          args.run_id,
        "time_utc":        datetime.now(timezone.utc).isoformat(),
        "git_commit":      git_commit(),
        "python_version":  python_version(),
        "requirements_sha256": requirements_hash(),
        "inputs": [
            {
                "path":   str(zeros_path),
                "sha256": sha256(zeros_path) if zeros_path.exists() else "missing",
            }
        ],
        "closure_status":  closure_status,
        "instance": {
            "type":     os.environ.get("INSTANCE_TYPE", "local"),
            "spot":     os.environ.get("SPOT_INSTANCE", "false") == "true",
            "platform": platform.platform(),
        },
        "env": {
            "GITHUB_ACTIONS": os.environ.get("GITHUB_ACTIONS", "false"),
            "GITHUB_SHA":     os.environ.get("GITHUB_SHA", ""),
            "GITHUB_REF":     os.environ.get("GITHUB_REF", ""),
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(state, indent=2))
    print(json.dumps({k: state[k] for k in
          ("run_id", "git_commit", "closure_status", "time_utc")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
