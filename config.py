"""
Central configuration — loaded from .env via python-dotenv.
Import this module anywhere to access shared settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent
DATA_RAW = ROOT_DIR / "data" / "raw"
DATA_PROCESSED = ROOT_DIR / "data" / "processed"
DATA_BACKUP = ROOT_DIR / "data" / "backup"

# ── Credentials ────────────────────────────────────────────────────────────
SPACETRACK_USERNAME = os.getenv("SPACETRACK_USERNAME", "")
SPACETRACK_PASSWORD = os.getenv("SPACETRACK_PASSWORD", "")

# ── API endpoints ──────────────────────────────────────────────────────────
SPACETRACK_BASE_URL = "https://www.space-track.org"
CELESTRAK_BASE_URL = "https://celestrak.org"

# ── Database ───────────────────────────────────────────────────────────────
DB_PATH = ROOT_DIR / "data" / "orbital_credit.db"

# ── Scoring thresholds ─────────────────────────────────────────────────────
RISK_HIGH_THRESHOLD = 0.7
RISK_MEDIUM_THRESHOLD = 0.4

DISPOSAL_COMPLIANCE_YEARS = 25  # ITU/FCC standard post-mission disposal window
