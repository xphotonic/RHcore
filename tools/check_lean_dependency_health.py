#!/usr/bin/env python3
"""Lean dependency/toolchain health checks for CI and local runs."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    toolchain_path = ROOT / "lean-toolchain"
    manifest_path = ROOT / "lake-manifest.json"
    mathlib_toolchain_path = ROOT / ".lake" / "packages" / "mathlib" / "lean-toolchain"

    if not toolchain_path.exists():
        return fail("lean-toolchain file is missing")
    if not manifest_path.exists():
        return fail("lake-manifest.json is missing")

    root_toolchain = toolchain_path.read_text(encoding="utf-8").strip()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    packages = manifest.get("packages", [])
    if not isinstance(packages, list):
        return fail("lake-manifest.json has invalid packages field")

    mathlib_pkg = next((p for p in packages if p.get("name") == "mathlib"), None)
    if mathlib_pkg is None:
        return fail("mathlib dependency not found in lake-manifest.json")
    if mathlib_pkg.get("type") != "git":
        return fail("mathlib dependency must be git-based (not path) for reproducible CI")

    path_pkgs = [p.get("name", "<unknown>") for p in packages if p.get("type") == "path"]
    if path_pkgs:
        return fail(f"path dependencies present in manifest: {', '.join(path_pkgs)}")

    if mathlib_toolchain_path.exists():
        mathlib_toolchain = mathlib_toolchain_path.read_text(encoding="utf-8").strip()
        if mathlib_toolchain != root_toolchain:
            return fail(
                "toolchain mismatch: "
                f"project={root_toolchain} vs mathlib={mathlib_toolchain}"
            )

    print("PASS: lean dependency health check")
    print(f"toolchain={root_toolchain}")
    print(f"mathlib_rev={mathlib_pkg.get('rev', '<unknown>')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
