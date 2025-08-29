#!/bin/bash
# Start TGW with symlinked models directory (Method B)

source "$(dirname "$0")/env.sh"

echo "🚀 Starting TGW with symlink method..."

# Create symlink first
"$(dirname "$0")/link_models.sh"

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

# Start TGW normally (models already linked)
python server.py \
    --api \
    --listen \
    --verbose

echo "🛑 TGW stopped"
