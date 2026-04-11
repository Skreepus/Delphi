# Delphi – Space Risk Radar (web UI)

Single-page **Cesium** globe + detail panel, backed by FastAPI `GET /api/satellites` (reads `data/processed/satellite_risk_enriched.csv`).

## Run (development)

1. From the **repository root**, start the API:

   ```bash
   .venv\Scripts\uvicorn api.main:app --reload --port 8000
   ```

2. In another terminal, start Vite:

   ```bash
   cd web
   npm install
   npm run dev
   ```

3. Open **http://localhost:5173**

Optional: set `VITE_API_URL` in `web/.env` if the API is not on `http://127.0.0.1:8000`.

## Build

```bash
cd web
npm run build
```

**Production behind nginx** (same host as Streamlit + API): use the deploy build so assets load under `/radar/`:

```bash
npm run build:deploy
```

See **[deploy/gcp/README.md](../deploy/gcp/README.md)** for the full VM setup.

Serve `web/dist` with any static host; configure CORS on the API for that origin (or set `DELPHI_CORS_ORIGINS` in `.env`). If you embed the radar in Streamlit, the static host must allow framing (e.g. `Content-Security-Policy: frame-ancestors *` or your Streamlit origin); the dev server sets this in `vite.config.ts`.

**API URL:** in development, the app calls `http://127.0.0.1:8000` by default. In production builds, if `VITE_API_URL` is unset, requests use the **same origin** (`/api/...`), which matches the nginx layout in `deploy/gcp/`.

## Streamlit Explorer

The main Delphi app embeds this UI on the **Explorer** page. With API + Vite running as above, open Streamlit and go to Explorer — it loads `http://localhost:5173` by default (same host string as the Vite “Local” URL). If you only open the radar at `http://127.0.0.1:5173`, set **`DELPHI_RADAR_URL=http://127.0.0.1:5173`** so the iframe matches. For a deployed build, set **`DELPHI_RADAR_URL`** to that URL.
