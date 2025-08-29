#!/bin/bash
# Start TGW with --model-dir flag (Method A)

source "$(dirname "$0")/env.sh"

echo "🚀 Starting TGW with flag method..."
echo "   Model directory: $TGW_MODELS_DIR"
echo "   UI: http://localhost:7860"
echo "   API: http://localhost:5000"

cd "$TGW_REPO"

# Activate conda environment
if [ ! -z "$CONDA_DEFAULT_ENV" ] && [ "$CONDA_DEFAULT_ENV" != "env-ai" ]; then
    echo "🔄 Switching to env-ai..."
    conda deactivate
fi

if [ "$CONDA_DEFAULT_ENV" != "env-ai" ]; then
    conda activate env-ai
fi

# Start TGW with model directory flag
python server.py \
    --model-dir "$TGW_MODELS_DIR" \
    --api \
    --listen \
    --verbose

echo "🛑 TGW stopped"
