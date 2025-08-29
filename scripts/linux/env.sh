#!/usr/bin/env bash
set -euo pipefail

# ===== Editable defaults (override via env) =====
: "${AI_CACHE_ROOT:="$HOME/AI_LLM_projects/ai_warehouse"}"
: "${REPO:="$HOME/AI_LLM_projects/text-generation-webui"}"  # 改成你的TGW repo路徑
: "${TGW_MODELS_DIR:="$AI_CACHE_ROOT/cache/models/llm"}"

# HuggingFace / Torch caches (共享倉集中管理)
export HF_HOME="${AI_CACHE_ROOT}/cache/hf"
export TRANSFORMERS_CACHE="${HF_HOME}/transformers"
export HF_DATASETS_CACHE="${HF_HOME}/datasets"
export HUGGINGFACE_HUB_CACHE="${HF_HOME}/hub"
export TORCH_HOME="${AI_CACHE_ROOT}/cache/torch"

# 建立必要目錄
mkdir -p "${TGW_MODELS_DIR}" \
         "${HF_HOME}" "${TRANSFORMERS_CACHE}" "${HF_DATASETS_CACHE}" "${HUGGINGFACE_HUB_CACHE}" \
         "${TORCH_HOME}"

echo "[env] AI_CACHE_ROOT=${AI_CACHE_ROOT}"
echo "[env] TGW_MODELS_DIR=${TGW_MODELS_DIR}"
echo "[env] REPO=${REPO}"
