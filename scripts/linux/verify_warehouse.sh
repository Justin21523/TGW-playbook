#!/bin/bash
# Verify warehouse setup and show contents (FIXED VERSION)

# Get script directory and source env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/env.sh"

echo "🔍 TGW Warehouse Verification"
echo "============================"

echo "📊 Directory Status:"
directories=(
    "$AI_CACHE_ROOT"
    "$TGW_MODELS_DIR"
    "$TGW_REPO"
    "$TGW_PLAYBOOK"
)

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        size=$(du -sh "$dir" 2>/dev/null | cut -f1)
        echo "  ✅ $dir ($size)"
    else
        echo "  ❌ $dir (missing)"
    fi
done

echo ""
echo "📦 Models in warehouse:"
if [ -d "$TGW_MODELS_DIR" ] && [ "$(ls -A "$TGW_MODELS_DIR" 2>/dev/null)" ]; then
    echo "  Location: $TGW_MODELS_DIR"
    find "$TGW_MODELS_DIR" -name "*.gguf" -printf "  ✅ %f (%s bytes)\n" 2>/dev/null
    find "$TGW_MODELS_DIR" -name "*.bin" -printf "  ✅ %f (%s bytes)\n" 2>/dev/null
    find "$TGW_MODELS_DIR" -name "*.safetensors" -printf "  ✅ %f (%s bytes)\n" 2>/dev/null
else
    echo "  ❌ No models found (download some first)"
fi

echo ""
echo "🗄️ HuggingFace Cache:"
if [ -d "$HF_HOME" ]; then
    cache_size=$(du -sh "$HF_HOME" 2>/dev/null | cut -f1)
    echo "  Cache location: $HF_HOME"
    echo "  Cache size: $cache_size"

    # Show recent downloads
    recent_files=$(find "$HF_HOME" -name "*.gguf" -o -name "*.bin" -o -name "*.safetensors" 2>/dev/null | head -3)
    if [ -n "$recent_files" ]; then
        echo "  Recent files:"
        echo "$recent_files" | sed 's/^/    /'
    fi
else
    echo "  ❌ No HF cache found"
fi

echo ""
echo "🔧 Environment Variables:"
echo "  AI_CACHE_ROOT: $AI_CACHE_ROOT"
echo "  TGW_MODELS_DIR: $TGW_MODELS_DIR"
echo "  TGW_REPO: $TGW_REPO"
echo "  CONDA_DEFAULT_ENV: $CONDA_DEFAULT_ENV"