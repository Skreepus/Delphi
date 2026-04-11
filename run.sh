#!/usr/bin/env bash
# Delphi: API + Explorer (Vite) + Streamlit — installs missing deps, starts all services.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo ""
echo "=== Delphi: full stack (API + Explorer + Streamlit) ==="
echo ""

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "[Delphi] Python 3 is required."
  exit 1
fi

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo "[Delphi] Node.js and npm are required. https://nodejs.org/"
  exit 1
fi

echo "[Delphi] Upgrading pip and installing Python packages..."
"$PY" -m pip install --upgrade pip -q
"$PY" -m pip install -r "$ROOT/requirements.txt"

echo "[Delphi] Installing Radar / Explorer npm packages..."
cd "$ROOT/web"
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi
cd "$ROOT"

API_PID=""
WEB_PID=""
stop_children() {
  [[ -n "$API_PID" ]] && kill "$API_PID" 2>/dev/null || true
  [[ -n "$WEB_PID" ]] && kill "$WEB_PID" 2>/dev/null || true
  wait "$API_PID" 2>/dev/null || true
  wait "$WEB_PID" 2>/dev/null || true
}
trap 'stop_children; exit 130' INT
trap 'stop_children; exit 143' TERM

echo ""
echo "[Delphi] Starting API      - http://127.0.0.1:8000"
"$PY" -m uvicorn api.main:app --host 127.0.0.1 --port 8000 &
API_PID=$!

echo "[Delphi] Starting Explorer - http://127.0.0.1:5173"
(cd "$ROOT/web" && exec npm run dev) &
WEB_PID=$!

echo "[Delphi] Waiting for API and Vite to bind..."
sleep 8

export DELPHI_RADAR_URL=http://127.0.0.1:5173
echo ""
echo "[Delphi] Starting website  - Streamlit (foreground)"
echo "[Delphi] Open http://localhost:8501 in your browser."
echo "[Delphi] Press Ctrl+C to stop Streamlit, API, and Explorer."
echo ""

set +e
"$PY" -m streamlit run app.py
ST=$?
set -e

trap - INT TERM
stop_children
exit "$ST"
