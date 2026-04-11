#!/usr/bin/env bash
# Delphi — install on Ubuntu/Debian (e.g. Google Cloud VM) with nginx + systemd.
# Run as a normal user with sudo; do not run as root only.
#
# Usage (from repo clone):
#   chmod +x deploy/gcp/install.sh
#   ./deploy/gcp/install.sh
#
# Optional: DELPHI_REPO=/path/to/Delphi to override auto-detected repo root.

set -euo pipefail

if [[ "${EUID:-}" -eq 0 ]]; then
  echo "Run this script as a normal user (with sudo). It will prompt for sudo when needed."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${DELPHI_REPO:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
RUN_USER="${SUDO_USER:-$(id -un)}"

if [[ ! -f "$REPO/app.py" ]] || [[ ! -f "$REPO/requirements.txt" ]]; then
  echo "Could not find Delphi repo at: $REPO"
  echo "Set DELPHI_REPO to the directory that contains app.py"
  exit 1
fi

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing: $1 — install it first."
    exit 1
  }
}

need_cmd python3
need_cmd node
need_cmd npm
need_cmd sudo

echo "=== Delphi GCP install ==="
echo "Repo:    $REPO"
echo "Service user: $RUN_USER"
echo ""

sudo apt-get update -qq
sudo apt-get install -y nginx rsync

cd "$REPO"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

pushd web >/dev/null
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi
npm run build:deploy
popd >/dev/null

sudo mkdir -p /var/www/delphi
sudo rsync -a --delete "$REPO/web/dist/" /var/www/delphi/radar/

sudo cp "$SCRIPT_DIR/nginx-delphi.conf" /etc/nginx/sites-available/delphi
if [[ -L /etc/nginx/sites-enabled/default ]]; then
  sudo rm -f /etc/nginx/sites-enabled/default
fi
sudo ln -sf /etc/nginx/sites-available/delphi /etc/nginx/sites-enabled/delphi
sudo nginx -t
sudo systemctl enable --now nginx

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

sudo systemctl daemon-reload
sudo systemctl enable --now delphi-api delphi-streamlit

echo ""
echo "=== Done ==="
echo "Nginx listens on port 80. Services:"
echo "  - delphi-api      (127.0.0.1:8000)"
echo "  - delphi-streamlit (127.0.0.1:8501)"
echo ""
echo "1. Point DNS or ngrok at this VM's port 80 (e.g. ngrok http 80)."
echo "2. Copy .env.example to .env and set (use your real public https origin, no trailing slash):"
echo "     DELPHI_PUBLIC_BASE=https://YOUR_HOST"
echo "     DELPHI_RADAR_URL=https://YOUR_HOST/radar/"
echo "     DELPHI_CORS_ORIGINS=https://YOUR_HOST"
echo "3. sudo systemctl restart delphi-api delphi-streamlit"
echo ""
echo "After code or web changes on the VM, run: ./deploy/gcp/update.sh"
