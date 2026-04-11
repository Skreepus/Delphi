# Deploy Delphi on Google Cloud (Ubuntu VM)

One **nginx** on port **80** serves:

| Path | Service |
|------|---------|
| `/` | Streamlit |
| `/api/`, `/media/` | FastAPI |
| `/radar/` | Built Cesium app (`npm run build:deploy`) |

**Explorer (Cesium globe):** Streamlit **explorer** embeds the radar UI. That iframe loads `DELPHI_RADAR_URL` (must be your public `https://…/radar/` when using ngrok). The radar page calls `/api/satellites` on the **same** host, so nginx + correct `.env` must match your public URL.

---

## Step-by-step: new Google Cloud VM (24/7 + ngrok)

### 1. Create the VM (console)

1. In [Google Cloud Console](https://console.cloud.google.com/) → **Compute Engine** → **VM instances** → **Create instance**.
2. **Region/zone:** pick one close to you; any zone is fine.
3. **Machine type:** `e2-medium` (2 vCPU) is comfortable for Streamlit + Node build; `e2-small` can work but builds are slower.
4. **Boot disk:** **Ubuntu 22.04 LTS** (or newer Ubuntu LTS), **40 GB** or more (Cesium `web/dist` + assets are large).
5. **Firewall:** enable **Allow HTTP traffic** only if you plan to hit the VM’s public IP on port 80. With **ngrok**, the public URL tunnels to local port 80; you do **not** need to open port 80 on the Google firewall for the internet to reach the app (ngrok uses outbound connections). SSH still needs the default SSH rule (or IAP).
6. **Availability:** for always-on, do **not** use a preemptible/spot VM. Optional: turn on **Live migration** / automatic restart if the host is maintained (instance settings).

### 2. SSH in and install basics

Use the browser SSH button or `gcloud compute ssh`.

```bash
sudo apt-get update
```

### 3. ngrok account and token

1. Sign up at [ngrok](https://ngrok.com/), open the dashboard, and copy your **Authtoken**.
2. Never commit this token. Prefer `deploy/gcp/ngrok.local.env` (see below).

### 4. Clone Delphi on the VM

```bash
cd ~
git clone https://github.com/YOUR_ORG/Delphi.git Delphi
cd Delphi
```

Use your real repo URL. If the repo is private, use SSH keys or a credential helper.

### 5. Data files (required for a non-empty explorer/API)

The API and explorer read processed outputs (see the main [README](../../README.md)). Ensure `data/processed/` contains the expected CSVs (e.g. from your pipeline or copied from your laptop with `scp`/`rsync`). Without them, the app runs but satellite views may be empty.

### 6. Run the installer (with ngrok)

From the **repository root** (`~/Delphi`):

```bash
chmod +x deploy/gcp/install.sh deploy/gcp/update.sh deploy/gcp/print-ngrok-url.sh
```

**Option A — token in the environment (simple):**

```bash
NGROK_AUTHTOKEN='paste-your-token-here' ./deploy/gcp/install.sh
```

**Option B — token in a gitignored file (better for history):**

```bash
cp deploy/gcp/ngrok.env.example deploy/gcp/ngrok.local.env
nano deploy/gcp/ngrok.local.env   # set NGROK_AUTHTOKEN=...
set -a && source deploy/gcp/ngrok.local.env && set +a && ./deploy/gcp/install.sh
```

The script installs nginx, Python venv + dependencies, Node 20 if needed, builds the radar, installs systemd units, and starts **delphi-api**, **delphi-streamlit**, **nginx**, and **delphi-ngrok**.

### 7. Get your public HTTPS URL

Wait ~5–10 seconds, then:

```bash
./deploy/gcp/print-ngrok-url.sh
```

Copy the printed `https://….ngrok-free.app` (or your paid domain).

### 8. Configure `.env` and restart (explorer + home video + CORS)

```bash
cp .env.example .env
nano .env
```

Set these three lines to that same origin (**no trailing slash** on `DELPHI_PUBLIC_BASE`; **`/radar/`** on the radar URL):

```env
DELPHI_PUBLIC_BASE=https://YOUR-SUBDOMAIN.ngrok-free.app
DELPHI_RADAR_URL=https://YOUR-SUBDOMAIN.ngrok-free.app/radar/
DELPHI_CORS_ORIGINS=https://YOUR-SUBDOMAIN.ngrok-free.app
```

Then:

```bash
sudo systemctl restart delphi-api delphi-streamlit
```

### 9. Verify in the browser

1. Open your ngrok `https://…` URL (root `/`) — Streamlit home should load; hero video should work if `assets/stars.mp4` exists and `DELPHI_PUBLIC_BASE` is correct.
2. Click **explorer** — the Cesium globe should load inside the page; data comes from `/api/satellites`.
3. Optional: open `https://…/radar/` directly — same radar UI full-page.
4. Optional: open `https://…/api/health` — should return JSON `{"status":"ok"}`.

### 10. Keep it running 24/7

- **systemd** units use `Restart=always` and `StartLimitIntervalSec=0` so services keep coming back after crashes or reboot (ngrok and nginx are enabled too).
- **Reboot:** `sudo reboot` — services should start automatically. On **ngrok free**, the **public URL may change** after restart; run `print-ngrok-url.sh` again and update `.env`, then `sudo systemctl restart delphi-api delphi-streamlit`. For a **stable URL**, use an ngrok **reserved domain** (paid) or another tunnel product.
- **ngrok free interstitial:** first-time visitors may see ngrok’s browser warning; after continuing, the app and iframe should behave normally.
- **Updates:** after `git push`, on the VM run `./deploy/gcp/update.sh`. Do **not** restart `delphi-ngrok` unless you accept a possible new free URL.

### 11. If something fails

```bash
sudo systemctl status delphi-api delphi-streamlit delphi-ngrok nginx --no-pager
journalctl -u delphi-api -u delphi-streamlit -u delphi-ngrok -n 80 --no-pager
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1/
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1/radar/
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1/api/health
```

---

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

If you pulled changes that modify `deploy/gcp/*.service` or `nginx-delphi.conf`, re-run **`./deploy/gcp/install.sh`** once (with the same `NGROK_AUTHTOKEN` / `ngrok.local.env` flow if you use ngrok) so systemd and nginx pick up the new files, then `sudo systemctl daemon-reload` is applied inside that script path — the installer already rewrites units and reloads nginx.

## Prerequisites

- Ubuntu 22.04+ (or Debian-based)
- `python3`, `python3-venv`, `git`, `sudo`
- Processed data under `data/processed/` (see main [README](../../README.md))

## Local development

Unchanged: `./run.sh` / `run.bat` (Vite on 5173, no nginx).
