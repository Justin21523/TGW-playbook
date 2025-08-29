#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=env.sh
source "${SCRIPT_DIR}/env.sh"

cd "${REPO}"
# 可把常用旗標寫到 user_data/CMD_FLAGS.txt，這裡示範直接命令列
python3 server.py \
  --model-dir "${TGW_MODELS_DIR}" \
  --api --listen --listen-host 0.0.0.0 --api-port 5000
