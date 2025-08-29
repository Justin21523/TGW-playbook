#!/usr/bin/env bash
set -euo pipefail

# Detect WSL
IS_WSL=0
if grep -qi microsoft /proc/sys/kernel/osrelease 2>/dev/null; then IS_WSL=1; fi

# Convert Windows or /c/... to /mnt/c/...
to_wsl_path() {
  local p="$1"
  if [[ $IS_WSL -eq 1 ]]; then
    if [[ "$p" =~ ^[A-Za-z]:\\ ]]; then wslpath -u "$p"; return; fi
    if [[ "$p" =~ ^/[a-zA-Z]/ ]]; then echo "/mnt/${p:1}"; return; fi
  fi
  echo "$p"
}

# Defaults → Windows C: (as /mnt/c)
: "${AI_CACHE_ROOT:="/mnt/c/AI_LLM_projects/ai_warehouse"}"
: "${REPO:="/mnt/c/AI_LLM_projects/text-generation-webui"}"
: "${TGW_MODELS_DIR:="${AI_CACHE_ROOT}/cache/models/llm"}"

AI_CACHE_ROOT="$(to_wsl_path "$AI_CACHE_ROOT")"
REPO="$(to_wsl_path "$REPO")"
TGW_MODELS_DIR="$(to_wsl_path "$TGW_MODELS_DIR")"

# HF/Torch caches into warehouse
export HF_HOME="${AI_CACHE_ROOT}/cache/hf"
export TRANSFORMERS_CACHE="${HF_HOME}/transformers"
export HF_DATASETS_CACHE="${HF_HOME}/datasets"
export HUGGINGFACE_HUB_CACHE="${HF_HOME}/hub"
export TORCH_HOME="${AI_CACHE_ROOT}/cache/torch"

mkdir -p "${TGW_MODELS_DIR}" "${HF_HOME}" "${TRANSFORMERS_CACHE}" \
         "${HF_DATASETS_CACHE}" "${HUGGINGFACE_HUB_CACHE}" "${TORCH_HOME}"

# Auto-activate env-ai (conda or venv)
if command -v conda >/dev/null 2>&1; then
  eval "$(conda shell.bash hook)"; conda activate env-ai || true
elif [[ -d "$HOME/.venvs/env-ai" ]]; then
  # shellcheck disable=SC1091
  source "$HOME/.venvs/env-ai/bin/activate"
fi

echo "[env] IS_WSL=${IS_WSL}"
echo "[env] AI_CACHE_ROOT=${AI_CACHE_ROOT}"
echo "[env] TGW_MODELS_DIR=${TGW_MODELS_DIR}"
echo "[env] REPO=${REPO}"
python3 -V || true
