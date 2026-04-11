#!/usr/bin/env bash
# Pull latest code, refresh deps, rebuild radar UI, sync static files, restart services.
# Run from repo root: ./deploy/gcp/update.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${DELPHI_REPO:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

cd "$REPO"
git pull

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

sudo rsync -a --delete "$REPO/web/dist/" /var/www/delphi/radar/
sudo chmod -R a+rX /var/www/delphi/radar
sudo systemctl restart delphi-api delphi-streamlit

echo "Update complete. delphi-api and delphi-streamlit restarted."
echo "Note: do not restart delphi-ngrok after deploy unless you must — free ngrok URLs often change on agent restart; update .env if the URL changes."
