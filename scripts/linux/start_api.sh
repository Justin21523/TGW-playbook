#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=env.sh
source "${SCRIPT_DIR}/env.sh"

cd "${REPO}"
# 如需 basic auth：加 --api-key YOUR_KEY
python3 server.py --nowebui \
  --model-dir "${TGW_MODELS_DIR}" \
  --api --listen --listen-host 0.0.0.0 --api-port 5000
