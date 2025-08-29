#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/env.sh"

# 如果沒有任何模型，先補一個小GGUF
DEF_REPO="Qwen/Qwen2.5-1.5B-Instruct-GGUF"
DEF_FILE="Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
if [[ ! -f "${TGW_MODELS_DIR}/${DEF_FILE}" ]]; then
  echo "[boot] No model found. Downloading ${DEF_FILE}..."
  "${SCRIPT_DIR}/download_model.sh" "${DEF_REPO}" "${DEF_FILE}"
fi

cd "${REPO}"
mkdir -p user_data
nohup python3 server.py \
  --model-dir "${TGW_MODELS_DIR}" \
  --api --api-port 5000 \
  --listen --listen-host 0.0.0.0 --port 7860 \
  > user_data/tgw.log 2>&1 &

# 等 UI 啟動
echo "[boot] Waiting for http://127.0.0.1:7860 ..."
for i in {1..60}; do
  if curl -fsS "http://127.0.0.1:7860" >/dev/null 2>&1; then
    echo "[boot] UI is up."; break
  fi; sleep 1
done

# 在 WSL 用 Windows 瀏覽器開頁面
if grep -qi microsoft /proc/sys/kernel/osrelease; then
  /mnt/c/Windows/explorer.exe "http://127.0.0.1:7860" >/dev/null 2>&1 || true
fi

echo "[ready] UI : http://127.0.0.1:7860"
echo "[ready] API: http://127.0.0.1:5000"
