#!/bin/bash
# TGW Environment Variables (Linux/WSL)

export AI_CACHE_ROOT="/mnt/c/AI_LLM_projects/ai_warehouse"
export HF_HOME="$AI_CACHE_ROOT/cache/hf"
export TRANSFORMERS_CACHE="$AI_CACHE_ROOT/cache/hf/transformers"
export HF_DATASETS_CACHE="$AI_CACHE_ROOT/cache/hf/datasets"
export HUGGINGFACE_HUB_CACHE="$AI_CACHE_ROOT/cache/hf/hub"
export TORCH_HOME="$AI_CACHE_ROOT/cache/torch"

export TGW_MODELS_DIR="$AI_CACHE_ROOT/cache/models/llm"
export TGW_REPO="/mnt/c/AI_LLM_projects/text-generation-webui"
export TGW_PLAYBOOK="/mnt/c/AI_LLM_projects/tgw-playbook"

echo "🔧 TGW environment variables loaded"
echo "   AI_CACHE_ROOT: $AI_CACHE_ROOT"
echo "   TGW_MODELS_DIR: $TGW_MODELS_DIR"
