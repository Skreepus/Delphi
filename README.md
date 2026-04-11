# Delphi

**Predictive compliance and disposal-risk insight for satellite operations**

Delphi combines the UCS Satellite Database, CelesTrak SATCAT, and optional Space-Track decay data into a single catalogue, assigns historical compliance labels, scores operators (DRCS / reliability), and estimates per-satellite risk. The primary interface is a Streamlit app (`app.py`); an optional FastAPI backend and Vite/Cesium “Space Risk Radar” explorer are included for demos.

---

## Quick start (dashboard only)

From the repository root:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501). Use the top navigation: **compare**, **rankings**, **explorer**, **overview**, **about us**.

You need processed CSVs under `data/processed/` (see [docs/METHODOLOGY.md](docs/METHODOLOGY.md)). Without them, operator and satellite views show empty states.

---

## Environment variables

Copy `.env.example` to `.env` and adjust if you use Space-Track ingestion or custom radar URL:

| Variable | Purpose |
|----------|---------|
| `SPACETRACK_USERNAME` / `SPACETRACK_PASSWORD` | Optional; for pulling decay data into `data/raw/spacetrack_decay.csv` via `src/ingestion/spacetrack_client.py` |
| `DELPHI_RADAR_URL` | Origin of the embedded radar UI (default `http://localhost:5173` for Vite dev) |
| `DELPHI_PUBLIC_BASE` | Public site origin with no trailing slash (e.g. `https://your-host`). Sets the home hero video URL for remote viewers (`/media/stars.mp4` on FastAPI). |
| `DELPHI_CORS_ORIGINS` | Comma-separated extra origins allowed by FastAPI CORS (e.g. your ngrok HTTPS URL). |

---

## Deploy on Google Cloud / Ubuntu (nginx + systemd)

From the repo root on the VM:

```bash
chmod +x deploy/gcp/install.sh deploy/gcp/update.sh deploy/gcp/print-ngrok-url.sh
NGROK_AUTHTOKEN='your-token' ./deploy/gcp/install.sh
```

Full steps, `.env` lines, and updates: **[deploy/gcp/README.md](deploy/gcp/README.md)**. Never commit ngrok tokens; rotate any token that was exposed.

---

## Data pipeline (from scratch)

Run **from the repository root** so `config` and paths resolve.

1. **Raw inputs** (place under `data/raw/`):
   - `ucs_satellite_database.xlsx` — [UCS satellite database](https://www.ucsusa.org/resources/satellite-database)
   - `satcat.csv` — CelesTrak SATCAT export
   - `spacetrack_decay.csv` — Space-Track decay query (optional but used in `run_pipeline.py`)

2. **Merge and splits**

   ```bash
   python run_pipeline.py
   ```

   Writes `master_satellites.csv`, `active_satellites.csv`, `dead_in_orbit.csv`, `historical_decayed.csv`, `boxscore.csv`.

3. **Compliance labels** (FCC-style five-year disposal window; see methodology)

   ```bash
   python src/scoring/labels.py
   ```

4. **Operator reliability scores** → `operator_scores.csv`

   ```bash
   python src/scoring/operator_reliability.py
   ```

5. **Satellite risk** — choose one path (or run heuristic first, then ML to refresh outputs):

   - **ML path** (logistic regression, recommended for explorer/overview):

     ```bash
     python src/features/feature_engineering.py
     python src/models/compliance_risk_model.py
     ```

     Writes `feature_table.csv`, `satellite_risk_scores.csv`, artefacts under `data/models/`, and triggers `satellite_risk_enriched.csv` when merge succeeds.

   - **Heuristic path** (no training):

     ```bash
     python src/scoring/risk_categories.py
     ```

     Writes heuristic `satellite_risk_scores.csv`. Enriched export:

     ```bash
     python utils/satellite_risk_merge.py
     ```

---

## Full stack (API + radar + Streamlit)

Requires **Node.js** and **npm** in addition to Python.

- **Windows:** `run.bat`
- **macOS/Linux:** `chmod +x run.sh && ./run.sh`

This installs dependencies, starts **uvicorn** on port **8000**, **Vite** on **5173**, then **Streamlit** on **8501**. Set `DELPHI_RADAR_URL` if the radar is hosted elsewhere.

---

## Optional UI assets

Place files in `assets/`:

| File | Used by |
|------|---------|
| `stars.mp4` | Home hero background |
| `sat1.jpg` | Operator compare page backdrop |
| `nasa1.jpg` | Operator rankings backdrop |
| `nasa2.jpg` | Satellite overview backdrop |

If an image is missing, that page simply omits the extra backdrop.

---

## Project structure

```
Delphi/
├── app.py                 # Streamlit entry + nav routing
├── config.py              # Paths, thresholds, env
├── api/main.py            # FastAPI JSON API for the radar UI
├── views/                 # Streamlit pages (home, compare, rankings, explorer, overview, about)
├── components/            # Shared Streamlit widgets / charts
├── utils/                 # Caching, satellite risk merge helpers
├── src/
│   ├── ingestion/         # UCS, SATCAT, Space-Track loaders
│   ├── cleaning/          # Normalisation, merge, SATCAT splits
│   ├── scoring/           # Labels, operator reliability, heuristic risk
│   ├── features/          # Feature table for the ML model
│   └── models/            # Logistic regression compliance-risk model
├── web/                   # Vite + Cesium explorer (npm)
├── data/
│   ├── raw/               # Inputs (gitignored — you supply)
│   └── processed/         # Pipeline outputs + enriched risk CSV
├── tests/                 # pytest
├── requirements.txt
├── run.bat / run.sh       # Full-stack dev launcher
├── deploy/gcp/            # nginx + systemd install for Linux / GCP VMs
└── docs/METHODOLOGY.md    # Scoring and modelling detail
```

Legacy multipage stubs under `pages/` are not wired by `app.py`; the live UI lives under `views/`.

---

## Tech stack

- **Python:** Streamlit, pandas, NumPy, scikit-learn, Plotly, FastAPI, uvicorn  
- **Web:** Node/Vite (explorer), Cesium (see `web/README.md`)

Further formulas, tiers, and limitations are documented in [docs/METHODOLOGY.md](docs/METHODOLOGY.md).
