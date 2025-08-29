#!/bin/bash
# Download models to shared warehouse (FIXED VERSION)

source "$(dirname "$0")/env.sh"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <model_repo> [specific_file]"
    echo "Examples:"
    echo "  $0 unsloth/Qwen2.5-VL-7B-Instruct-GGUF"
    echo "  $0 unsloth/Qwen2.5-VL-7B-Instruct-GGUF Qwen2.5-VL-7B-Instruct-Q5_K_M.gguf"
    exit 1
fi

MODEL_REPO="$1"
SPECIFIC_FILE="$2"

echo "⬇️  Downloading model to warehouse..."
echo "   Repository: $MODEL_REPO"
echo "   Target: $TGW_MODELS_DIR"

# Ensure target directory exists
mkdir -p "$TGW_MODELS_DIR"

cd "$TGW_REPO"

# Activate conda environment
if [ "$CONDA_DEFAULT_ENV" != "env-ai" ]; then
    echo "🔄 Activating env-ai..."
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate env-ai
fi

# Download with optional specific file
if [ -n "$SPECIFIC_FILE" ]; then
    echo "   Specific file: $SPECIFIC_FILE"
    python download-model.py "$MODEL_REPO" \
        --output "$TGW_MODELS_DIR" \
        --specific-file "$SPECIFIC_FILE"
else
    echo "   Downloading all files..."
    python download-model.py "$MODEL_REPO" \
        --output "$TGW_MODELS_DIR"
fi

echo "✅ Download completed. Checking files..."

# Manual verification instead of calling external script
echo ""
echo "📦 Downloaded files:"
if [ -d "$TGW_MODELS_DIR" ]; then
    find "$TGW_MODELS_DIR" -name "*.gguf" -o -name "*.bin" -o -name "*.safetensors" | tail -5
    echo ""
    echo "📊 Warehouse size: $(du -sh "$TGW_MODELS_DIR" | cut -f1)"
else
    echo "❌ Target directory not found: $TGW_MODELS_DIR"
fi