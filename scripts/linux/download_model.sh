#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=env.sh
source "${SCRIPT_DIR}/env.sh"

MODEL_REPO="${1:-Qwen/Qwen2.5-1.5B-Instruct-GGUF}"
MODEL_FILE="${2:-Qwen2.5-1.5B-Instruct-Q4_K_M.gguf}"

cd "${REPO}"
# 使用"連結法"時，download-model.py 會把檔案落在 ${REPO}/models -> ${TGW_MODELS_DIR}
python3 download-model.py "${MODEL_REPO}" --text-only || true
# 指定單檔（GGUF）下載
python3 download-model.py "${MODEL_REPO}" --filename "${MODEL_FILE}" || true

echo "[download] Expect file at: ${TGW_MODELS_DIR}/${MODEL_FILE}"
ls -lh "${TGW_MODELS_DIR}" | grep -E "${MODEL_FILE}" || true
