#!/usr/bin/env bash
# sync_toolchain.sh — sync lean-toolchain with mathlib4 and update manifest
set -euo pipefail

MATHLIB_TAG="${1:-v4.14.0}"
MATHLIB_URL="https://raw.githubusercontent.com/leanprover-community/mathlib4/${MATHLIB_TAG}"

echo "==> Syncing with mathlib4 ${MATHLIB_TAG}"

# 1. Pull mathlib4 toolchain
curl -sSL "${MATHLIB_URL}/lean-toolchain" -o lean-toolchain
echo "    lean-toolchain: $(cat lean-toolchain)"

# 2. Update lakefile to pin mathlib tag
sed -i "s|@ \"v[0-9.]*\"|@ \"${MATHLIB_TAG}\"|g" lakefile.lean
echo "    lakefile.lean: pinned to ${MATHLIB_TAG}"

# 3. Regenerate manifest
lake update
echo "    lake-manifest.json: regenerated"

# 4. Verify
echo "==> Build check"
lake build RhCore.Core.Carrier || echo "WARNING: build check failed — check imports"

echo "==> Done. Commit: lean-toolchain lakefile.lean lake-manifest.json"
