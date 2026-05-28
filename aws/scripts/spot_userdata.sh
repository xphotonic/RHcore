#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   sudo bash spot_userdata.sh <REPO_URL> <BUCKET> <PROJECT> <RUN_ID>

REPO_URL="${1:-}"
BUCKET="${2:-}"
PROJECT="${3:-myproj}"
RUN_ID="${4:-$(date -u +%Y%m%dT%H%M%SZ)}"

if [[ -z "$REPO_URL" || -z "$BUCKET" ]]; then
  echo "usage: spot_userdata.sh <REPO_URL> <BUCKET> [PROJECT] [RUN_ID]" >&2
  exit 2
fi

apt-get update -y
apt-get install -y git python3 python3-pip make curl

if ! command -v cosign >/dev/null 2>&1; then
  curl -sSL https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64 \
    -o /usr/local/bin/cosign
  chmod +x /usr/local/bin/cosign
fi

WORKDIR=/opt/repro
rm -rf "$WORKDIR"
git clone "$REPO_URL" "$WORKDIR"
cd "$WORKDIR/RhCore"

python3 -m pip install -r requirements.txt
make -f Makefile.repro RUN_ID="$RUN_ID" all
make -f Makefile.repro RUN_ID="$RUN_ID" BUCKET="$BUCKET" PROJECT="$PROJECT" push

