#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/env.sh"

MODEL_REPO="${1:-Qwen/Qwen2.5-1.5B-Instruct-GGUF}"
MODEL_FILE="${2:-Qwen2.5-1.5B-Instruct-Q4_K_M.gguf}"

if [[ -d "${REPO}" && -f "${REPO}/download-model.py" ]]; then
  echo "[download] via TGW downloader @ ${REPO}"
  cd "${REPO}"
  python3 download-model.py "${MODEL_REPO}" --text-only || true
  python3 download-model.py "${MODEL_REPO}" --filename "${MODEL_FILE}" || true
else
  echo "[fallback] huggingface_hub → ${TGW_MODELS_DIR}"
  python3 - <<'PY'
import os, sys
from huggingface_hub import hf_hub_download
repo, fn = sys.argv[1], sys.argv[2]
target = os.environ["TGW_MODELS_DIR"]
os.makedirs(target, exist_ok=True)
p = hf_hub_download(repo_id=repo, filename=fn,
                    local_dir=target, local_dir_use_symlinks=False,
                    cache_dir=os.environ.get("HF_HOME"))
print("[ok] downloaded:", p)
PY
fi

echo "[verify] ${TGW_MODELS_DIR}/${MODEL_FILE}"
ls -lh "${TGW_MODELS_DIR}" | grep -E "${MODEL_FILE}" || true
