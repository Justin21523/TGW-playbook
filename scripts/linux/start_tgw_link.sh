#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=env.sh
source "${SCRIPT_DIR}/env.sh"

# 先建立符號連結
"${SCRIPT_DIR}/link_models.sh"

cd "${REPO}"
python3 server.py \
  --api --listen --listen-host 0.0.0.0 --api-port 5000
