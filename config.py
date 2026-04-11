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
DB_PATH = ROOT_DIR / "data" / "orbital_credita.db"

# ── Existing processed files (inputs) ──────────────────────────────────────
MASTER_CSV = DATA_PROCESSED / "master_satellites.csv"
ACTIVE_SATELLITES_CSV = DATA_PROCESSED / "active_satellites.csv"
DEAD_IN_ORBIT_CSV = DATA_PROCESSED / "dead_in_orbit.csv"
HISTORICAL_DECAYED_CSV = DATA_PROCESSED / "historical_decayed.csv"
BOXSCORE_CSV = DATA_PROCESSED / "boxscore.csv"

# ── Scoring pipeline outputs ───────────────────────────────────────────────
LABELED_CSV = DATA_PROCESSED / "labeled_satellites.csv"
OPERATOR_SCORES_CSV = DATA_PROCESSED / "operator_scores.csv"
SATELLITE_RISK_CSV = DATA_PROCESSED / "satellite_risk_scores.csv"
SATELLITE_RISK_ENRICHED_CSV = DATA_PROCESSED / "satellite_risk_enriched.csv"
FEATURE_TABLE_CSV = DATA_PROCESSED / "feature_table.csv"

# ── Scoring thresholds ─────────────────────────────────────────────────────
RISK_HIGH_THRESHOLD = 0.7
RISK_MEDIUM_THRESHOLD = 0.4
DISPOSAL_COMPLIANCE_YEARS = 5

# ── Operator reliability scoring ───────────────────────────────────────────
COMPLIANCE_WEIGHT = 70
DEBRIS_WEIGHT = 30
MIN_OPERATOR_HISTORY = 3

RELIABILITY_TIERS = {
    "high": 70,
    "medium": 40,
    "low": 0,
}

# ── Active satellite status keywords ───────────────────────────────────────
ACTIVE_STATUSES = ["active", "operational"]

# ── Risk Categories ─────────────────────────────────────────
# Operator reliability thresholds
OPERATOR_RISK_THRESHOLDS = {
    "high_risk":   0.40,   # reliability below 0.40 → high risk
    "medium_risk": 0.70,   # reliability 0.40–0.70  → medium risk
                           # reliability above 0.70 → low risk
}

# Labels for display
RISK_LABELS = {
    "high":   "High Risk",
    "medium": "Medium Risk",
    "low":    "Low Risk",
}