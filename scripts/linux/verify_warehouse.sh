#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=env.sh
source "${SCRIPT_DIR}/env.sh"

echo "[verify] models under TGW_MODELS_DIR:"
tree -L 2 "${TGW_MODELS_DIR}" || ls -al "${TGW_MODELS_DIR}"

echo "[verify] HF caches:"
du -sh "${HF_HOME}"/* 2>/dev/null || true
