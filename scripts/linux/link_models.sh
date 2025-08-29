#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=env.sh
source "${SCRIPT_DIR}/env.sh"

# 把 <repo>/text-generation-webui/models -> TGW_MODELS_DIR
mkdir -p "${REPO}"
cd "${REPO}"

# 確保 TGW 子目錄存在
mkdir -p "${REPO}/user_data"  # TGW 會用到
rm -rf "${REPO}/models" 2>/dev/null || true
ln -sfn "${TGW_MODELS_DIR}" "${REPO}/models"

echo "[link] ${REPO}/models -> ${TGW_MODELS_DIR}"
ls -al "${REPO}/models"
