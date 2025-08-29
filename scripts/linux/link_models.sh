#!/bin/bash
# Create symlink: text-generation-webui/models -> shared warehouse

source "$(dirname "$0")/env.sh"

echo "🔗 Linking TGW models directory to warehouse"

if [ ! -d "$TGW_REPO" ]; then
    echo "❌ TGW repository not found: $TGW_REPO"
    exit 1
fi

cd "$TGW_REPO"

# Remove existing models directory/link
if [ -L "models" ]; then
    echo "  Removing existing symlink..."
    rm "models"
elif [ -d "models" ]; then
    echo "  Backing up existing models directory..."
    mv "models" "models.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Create symlink
ln -sf "$TGW_MODELS_DIR" "models"
echo "✅ Symlink created: models -> $TGW_MODELS_DIR"

# Verify
if [ -L "models" ] && [ -d "models" ]; then
    echo "✅ Symlink verification passed"
    ls -la models/
else
    echo "❌ Symlink verification failed"
    exit 1
fi
