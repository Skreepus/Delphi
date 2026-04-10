# Delphi

**A Predictive Compliance and Disposal-Risk Platform for Sustainable Satellite Operations**



---

## Quick Start

```bash
# 1. Clone and set up environment
git clone <repo-url> && cd orbital-credit
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure credentials
cp .env.example .env
# Edit .env with your Space-Track credentials

# 3. Run data pipeline (in order)
python -c "from src.ingestion.ucs_loader import load_ucs; load_ucs()"
# ... (see docs/METHODOLOGY.md for full pipeline steps)

# 4. Launch dashboard
streamlit run app.py
```

## Project Structure

```
orbital-credit/
├── app.py                    # Streamlit entry point
├── config.py                 # Central config (paths, thresholds, env vars)
├── pages/                    # Multipage Streamlit views
│   ├── 01_home.py
│   ├── 02_operator_rankings.py
│   ├── 03_satellite_rankings.py
│   ├── 04_operator_profile.py
│   └── 05_satellite_profile.py
├── src/
│   ├── ingestion/            # Data loaders (UCS, Space-Track, CelesTrak)
│   ├── cleaning/             # Normalisation, entity resolution, merging
│   ├── features/             # Feature engineering + sklearn pipeline
│   ├── models/               # Model training + evaluation
│   └── scoring/              # Labels, operator scores, satellite risk
├── components/               # Reusable Streamlit UI components
├── utils/                    # Caching helpers, display formatting
├── data/
│   ├── raw/                  # Raw source files (gitignored)
│   ├── processed/            # Cleaned + scored outputs
│   └── backup/               # Static CSV fallbacks for demo
├── tests/                    # pytest test suite
└── docs/METHODOLOGY.md       # Technical writeup
```

## Data Sources

| Source | Format | Access |
|--------|--------|--------|
| UCS Satellite Database | Excel | Free download |
| Space-Track.org | JSON/CSV API | Free account required |
| CelesTrak | CSV/TLE REST | Public, no auth |

## Tech Stack

See `docs/METHODOLOGY.md` for the full breakdown.
