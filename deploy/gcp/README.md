# Deploy Delphi on Google Cloud (or any Ubuntu VM)

One **nginx** entry on port **80** serves:

- **/** — Streamlit (`app.py`)
- **/api/** and **/media/** — FastAPI (radar JSON + hero video)
- **/radar/** — production build of the Cesium explorer (`npm run build:deploy`)

## Prerequisites

- Ubuntu 22.04+ (or similar Debian-based) VM
- `python3`, `python3-venv`, `git`
- Node.js 20+ and `npm` ([NodeSource](https://github.com/nodesource/distributions) if the distro package is too old)
- Processed data under `data/processed/` (see main [README](../../README.md))

## One-time install

From your clone of the repo:

```bash
chmod +x deploy/gcp/install.sh deploy/gcp/update.sh
./deploy/gcp/install.sh
```

The script installs system packages (`nginx`, `rsync`), creates `.venv`, runs `pip install`, builds the web UI with base path `/radar/`, copies static files to `/var/www/delphi/radar/`, installs nginx + systemd units, and starts services.

## Public URL (ngrok or load balancer)

Tunnel **port 80** (not 8501). Example:

```bash
ngrok http 80
```

Copy `.env.example` to `.env` in the repo root and set (replace with your HTTPS origin, **no trailing slash** on `DELPHI_PUBLIC_BASE`):

```env
DELPHI_PUBLIC_BASE=https://YOUR_SUBDOMAIN.ngrok-free.app
DELPHI_RADAR_URL=https://YOUR_SUBDOMAIN.ngrok-free.app/radar/
DELPHI_CORS_ORIGINS=https://YOUR_SUBDOMAIN.ngrok-free.app
```

Then:

```bash
sudo systemctl restart delphi-api delphi-streamlit
```

## Updates after `git push`

On the VM:

```bash
./deploy/gcp/update.sh
```

## Firewall

You only need **SSH** for admin if you use ngrok (outbound HTTPS). To expose nginx directly, open **80**/**443** in the cloud firewall.

## Local full stack (development)

Unchanged: use `./run.sh` or `run.bat` — Vite dev server on 5173, no nginx.
