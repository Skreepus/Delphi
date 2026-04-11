# Deploy Delphi on Google Cloud (Ubuntu VM)

One **nginx** on port **80** serves:

| Path | Service |
|------|---------|
| `/` | Streamlit |
| `/api/`, `/media/` | FastAPI |
| `/radar/` | Built Cesium app (`npm run build:deploy`) |

## One command (recommended)

SSH to the VM, clone the repo, then from the **repo root**:

```bash
chmod +x deploy/gcp/install.sh deploy/gcp/update.sh deploy/gcp/print-ngrok-url.sh
NGROK_AUTHTOKEN='paste-token-here' ./deploy/gcp/install.sh
```

- Installs **nginx**, **Node 20** (if missing), **ngrok** (if token provided), Python venv, builds the radar, copies files to `/var/www/delphi/radar/`, enables **delphi-api**, **delphi-streamlit**, and **delphi-ngrok**.
- Prints **smoke-test** HTTP codes for `/`, `/radar/`, and `/api/health`.

**Do not put your token in git.** To avoid typing it in shell history, use `deploy/gcp/ngrok.env.example` → copy to **`deploy/gcp/ngrok.local.env`** (gitignored), fill `NGROK_AUTHTOKEN`, then:

```bash
set -a && source deploy/gcp/ngrok.local.env && set +a && ./deploy/gcp/install.sh
```

If a token was ever leaked, **rotate it** in the [ngrok dashboard](https://dashboard.ngrok.com/).

### After install: `.env` for Streamlit / CORS / video

```bash
./deploy/gcp/print-ngrok-url.sh
```

Copy `.env.example` → `.env` in the repo root. Use the printed `https://…` URL (**no trailing slash** on `DELPHI_PUBLIC_BASE`):

```env
DELPHI_PUBLIC_BASE=https://YOUR-NGROK-SUBDOMAIN.ngrok-free.app
DELPHI_RADAR_URL=https://YOUR-NGROK-SUBDOMAIN.ngrok-free.app/radar/
DELPHI_CORS_ORIGINS=https://YOUR-NGROK-SUBDOMAIN.ngrok-free.app
```

```bash
sudo systemctl restart delphi-api delphi-streamlit
```

### Without ngrok

```bash
./deploy/gcp/install.sh
```

Expose port **80** with your cloud firewall or another tunnel, and set `.env` to that public URL.

## Updates after `git push`

```bash
./deploy/gcp/update.sh
```

## Prerequisites

- Ubuntu 22.04+ (or Debian-based)
- `python3`, `python3-venv`, `git`, `sudo`
- Processed data under `data/processed/` (see main [README](../../README.md))

## Local development

Unchanged: `./run.sh` / `run.bat` (Vite on 5173, no nginx).
