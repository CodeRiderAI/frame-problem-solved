#!/bin/bash
set -euo pipefail

# run from this script's directory
cd "$(dirname "$0")"

usage() {
  cat <<'USAGE'
Usage:
  ./replay.sh --check      # verify sample.log against sample.log.sha256
  ./replay.sh              # (committer only) re-generate sample.log.sha256
USAGE
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ "${1:-}" == "--check" ]]; then
  # Verification mode (recommended for all users)
  # Exits non-zero if verification fails.
  sha256sum -c proofpack/sample.log.sha256
  exit $?
fi

# Re-generation mode (for the original committer only)
# This updates the reference checksum. Do NOT run this in user environments.
sha256sum proofpack/sample.log > proofpack/sample.log.sha256
echo "[replay] sample.log.sha256 re-generated."