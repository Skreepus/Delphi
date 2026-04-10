"""
Run this once to build everything from your two source files.
Put this in a notebook or a script at the project root.
"""
import pandas as pd

from src.ingestion.celestrak import load_satcat
from src.ingestion.ucs_loader import load_ucs  # your existing UCS loader

from src.cleaning.normaliser import standardise_columns, normalise_operator_names, UCS_RENAME
from src.cleaning.satcat import (
    filter_payloads,
    split_active,
    split_dead_in_orbit,
    split_historical_decayed,
    build_boxscore,
)
from src.cleaning.merger import merge_datasets

# ── Step 1: Load raw data ─────────────────────────────
satcat = load_satcat("data/raw/satcat.csv")
ucs_raw = pd.read_excel("data/raw/ucs_satellite_database.xlsx")

# ── Step 2: Standardise UCS columns ───────────────────
ucs = standardise_columns(ucs_raw, UCS_RENAME)
ucs['operator_clean'] = normalise_operator_names(ucs['operator'])
ucs['norad_id'] = pd.to_numeric(ucs['norad_id'], errors='coerce')

# ── Step 3: Filter CelesTrak to payloads ──────────────
payloads = filter_payloads(satcat)

# ── Step 4: Merge UCS + CelesTrak ─────────────────────
master = merge_datasets(ucs, payloads)

# ── Step 5: Build subsets for scoring ──────────────────
active = split_active(payloads)
dead = split_dead_in_orbit(payloads)
historical = split_historical_decayed(payloads)
boxscore = build_boxscore(satcat)

# ── Step 6: Save everything ───────────────────────────
active.to_csv("data/processed/active_satellites.csv", index=False)
dead.to_csv("data/processed/dead_in_orbit.csv", index=False)
historical.to_csv("data/processed/historical_decayed.csv", index=False)
boxscore.to_csv("data/processed/boxscore.csv", index=False)

print("\nDone. All tables saved to data/processed/")