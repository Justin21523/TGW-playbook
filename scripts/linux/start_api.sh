#!/bin/bash
# Start TGW API only (no web UI)

source "$(dirname "$0")/env.sh"

API_PORT=${1:-5000}

echo "🔌 Starting TGW API-only mode..."
echo "   API endpoint: http://localhost:$API_PORT"
echo "   Model directory: $TGW_MODELS_DIR"

cd "$TGW_REPO"

# Activate conda environment
if [ "$CONDA_DEFAULT_ENV" != "env-ai" ]; then
    conda activate env-ai
fi

python server.py \
    --model-dir "$TGW_MODELS_DIR" \
    --nowebui \
    --api \
    --listen \
    --api-port "$API_PORT" \
    --verbose

echo "🛑 TGW API stopped"
