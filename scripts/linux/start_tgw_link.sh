#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=env.sh
source "${SCRIPT_DIR}/env.sh"

# 先建立符號連結
"${SCRIPT_DIR}/link_models.sh"

cd "${REPO}"
exec python3 server.py \
  --api --api-port 5000 \
  --listen --listen-host 0.0.0.0 --port 7860
