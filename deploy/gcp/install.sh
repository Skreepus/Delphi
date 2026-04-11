#!/usr/bin/env bash
# Delphi — one-shot install on Ubuntu/Debian (e.g. Google Cloud VM).
#
# From repo root:
#   chmod +x deploy/gcp/install.sh deploy/gcp/update.sh deploy/gcp/print-ngrok-url.sh
#   ./deploy/gcp/install.sh
#
# With ngrok (token never goes in git — pass only here):
#   NGROK_AUTHTOKEN='your-token' ./deploy/gcp/install.sh
#
# Optional: DELPHI_REPO=/path/to/Delphi
#
# Run as root (root@vm) or as a user with sudo. If you use `sudo ./install.sh` from
# ubuntu, services and files are owned by ubuntu (SUDO_USER).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${DELPHI_REPO:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

if [[ "${EUID:-}" -eq 0 ]]; then
  RUN_USER="${SUDO_USER:-root}"
else
  RUN_USER="$(id -un)"
fi

if [[ ! -f "$REPO/app.py" ]] || [[ ! -f "$REPO/requirements.txt" ]]; then
  echo "Could not find Delphi repo at: $REPO"
  echo "Set DELPHI_REPO to the directory that contains app.py"
  exit 1
fi

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || return 1
}

need_cmd sudo || {
  echo "Missing: sudo (required for nginx, /var/www, systemd)"
  exit 1
}

echo "=== Delphi GCP install ==="
echo "Repo:         $REPO"
echo "Service user: $RUN_USER"
echo ""

sudo apt-get update -qq
# python3-venv: required for `python3 -m venv` on minimal cloud images
# git: clone/pull; build-essential: some pip wheels compile on Linux
sudo apt-get install -y \
  nginx rsync curl ca-certificates gnupg \
  python3 python3-venv python3-pip git build-essential

if ! need_cmd node || ! need_cmd npm; then
  echo "[Delphi] Installing Node.js 20..."
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

if [[ -n "${NGROK_AUTHTOKEN:-}" ]]; then
  if ! need_cmd ngrok; then
    echo "[Delphi] Installing ngrok package..."
    curl -fsSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
      | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list >/dev/null
    sudo apt-get update -qq
    sudo apt-get install -y ngrok
  fi
fi

run_as_owner() {
  if [[ "${EUID:-}" -eq 0 ]] && [[ "$RUN_USER" != "root" ]]; then
    sudo -u "$RUN_USER" "$@"
  else
    "$@"
  fi
}

# Python venv, pip, npm build (files owned by RUN_USER when installing via sudo)
if [[ "${EUID:-}" -eq 0 ]] && [[ "$RUN_USER" != "root" ]]; then
  sudo -u "$RUN_USER" bash -s <<EOS
set -euo pipefail
cd "$REPO"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
cd web
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi
npm run build:deploy
EOS
else
  bash -s <<EOS
set -euo pipefail
cd "$REPO"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
cd web
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi
npm run build:deploy
EOS
fi

sudo mkdir -p /var/www/delphi/radar
sudo rsync -a --delete "$REPO/web/dist/" /var/www/delphi/radar/
sudo chmod -R a+rX /var/www/delphi/radar

sudo cp "$SCRIPT_DIR/nginx-delphi.conf" /etc/nginx/sites-available/delphi
if [[ -L /etc/nginx/sites-enabled/default ]]; then
  sudo rm -f /etc/nginx/sites-enabled/default
fi
sudo ln -sf /etc/nginx/sites-available/delphi /etc/nginx/sites-enabled/delphi
sudo nginx -t
sudo systemctl enable nginx
if sudo systemctl is-active --quiet nginx 2>/dev/null; then
  sudo systemctl reload nginx
else
  sudo systemctl start nginx
fi

substitute_unit() {
  local src="$1"
  local dest="$2"
  sed \
    -e "s|__DELPHI_USER__|$RUN_USER|g" \
    -e "s|__DELPHI_REPO__|$REPO|g" \
    "$src" | sudo tee "$dest" >/dev/null
}

substitute_unit "$SCRIPT_DIR/delphi-api.service" /etc/systemd/system/delphi-api.service
substitute_unit "$SCRIPT_DIR/delphi-streamlit.service" /etc/systemd/system/delphi-streamlit.service

if [[ -n "${NGROK_AUTHTOKEN:-}" ]]; then
  run_as_owner ngrok config add-authtoken "$NGROK_AUTHTOKEN" >/dev/null
  substitute_unit "$SCRIPT_DIR/delphi-ngrok.service" /etc/systemd/system/delphi-ngrok.service
  echo "[Delphi] ngrok authtoken saved for user: $RUN_USER"
fi

sudo systemctl daemon-reload
sudo systemctl enable --now delphi-api delphi-streamlit

if [[ -f /etc/systemd/system/delphi-ngrok.service ]]; then
  sudo systemctl enable --now delphi-ngrok
fi

echo ""
echo "=== Smoke tests (localhost) ==="
code_root="$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/ || true)"
code_radar="$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/radar/ || true)"
code_api="$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/api/health || true)"
echo "  GET /           -> HTTP $code_root  (expect 200)"
echo "  GET /radar/     -> HTTP $code_radar  (expect 200)"
echo "  GET /api/health -> HTTP $code_api  (expect 200)"

echo ""
echo "=== Done ==="
echo "Units: delphi-api, delphi-streamlit, nginx"
if [[ -f /etc/systemd/system/delphi-ngrok.service ]]; then
  echo "       delphi-ngrok"
  echo ""
  echo "Wait a few seconds, then show your public https URL:"
  echo "  $REPO/deploy/gcp/print-ngrok-url.sh"
  echo ""
  echo "Set $REPO/.env (copy from .env.example), then:"
  echo "  sudo systemctl restart delphi-api delphi-streamlit"
else
  echo ""
  echo "Optional: NGROK_AUTHTOKEN='...' ./deploy/gcp/install.sh  (or: ngrok http 80)"
  echo "Then set .env from .env.example and: sudo systemctl restart delphi-api delphi-streamlit"
fi
echo ""
echo "Updates: ./deploy/gcp/update.sh"
echo "Never commit ngrok tokens. Rotate any token that was pasted into chat or logs."
