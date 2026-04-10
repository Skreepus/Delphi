"""
Run this once to build all processed data from raw sources.
Combines UCS, CelesTrak, and Space-Track into one master table.
"""
import pandas as pd
from src.ingestion.celestrak import load_satcat
from src.ingestion.ucs_loader import load_ucs
from src.cleaning.normaliser import standardise_columns, normalise_operator_names, UCS_RENAME
from src.cleaning.entity_resolution import resolve_operators
from src.cleaning.satcat import (
    filter_payloads,
    split_active,
    split_dead_in_orbit,
    split_historical_decayed,
    build_boxscore,
)
from src.cleaning.merger import merge_datasets

# ── Step 1: Load all three raw sources ─────────────────
satcat = load_satcat("data/raw/satcat.csv")
ucs_raw = load_ucs()
spacetrack = pd.read_csv("data/raw/spacetrack_decay.csv")

# ── Step 2: Standardise UCS columns ───────────────────
ucs = standardise_columns(ucs_raw, UCS_RENAME)
ucs['norad_id'] = pd.to_numeric(ucs['norad_id'], errors='coerce')

# ── Step 3: Normalise operator names in UCS ────────────
ucs['operator_clean'] = normalise_operator_names(ucs['operator'])

# ── Step 4: Fuzzy match operator names ─────────────────
print("[pipeline] Running fuzzy operator matching...")
ucs['operator_resolved'] = resolve_operators(
    ucs['operator_clean'],
    ucs['operator_clean'],
    threshold=85,
)
print(f"[pipeline] Unique operators before: {ucs['operator_clean'].nunique()}")
print(f"[pipeline] Unique operators after:  {ucs['operator_resolved'].nunique()}")

# ── Step 5: Clean Space-Track data ─────────────────────
print(f"[pipeline] Space-Track loaded: {len(spacetrack)} rows")
spacetrack = spacetrack.rename(columns={
    'NORAD_CAT_ID': 'norad_id',
    'OBJECT_NUMBER': 'st_object_number',
    'OBJECT_NAME': 'st_object_name',
    'INTLDES': 'st_intldes',
    'OBJECT_ID': 'st_object_id',
    'RCS': 'st_rcs',
    'RCS_SIZE': 'st_rcs_size',
    'COUNTRY': 'st_country',
    'MSG_EPOCH': 'st_msg_epoch',
    'DECAY_EPOCH': 'st_decay_epoch',
    'SOURCE': 'st_source',
    'MSG_TYPE': 'st_msg_type',
    'PRECEDENCE': 'st_precedence',
})
spacetrack['norad_id'] = pd.to_numeric(spacetrack['norad_id'], errors='coerce')
spacetrack['st_decay_epoch'] = pd.to_datetime(spacetrack['st_decay_epoch'], errors='coerce')
spacetrack['st_msg_epoch'] = pd.to_datetime(spacetrack['st_msg_epoch'], errors='coerce')

# ── Step 6: Filter CelesTrak to payloads ──────────────
payloads = filter_payloads(satcat)

# ── Step 7: Merge all three sources ───────────────────
# First: UCS + CelesTrak
master = merge_datasets(ucs, payloads)

# Second: add Space-Track decay data
st_cols = ['norad_id', 'st_decay_epoch', 'st_rcs_size', 'st_country', 'st_source', 'st_msg_type']
master = master.merge(
    spacetrack[st_cols].drop_duplicates(subset='norad_id', keep='last'),
    on='norad_id',
    how='left',
)
st_match = master['st_decay_epoch'].notna().mean()
print(f"[pipeline] After Space-Track merge: {len(master)} rows")
print(f"[pipeline] Space-Track match rate: {st_match:.1%}")

# ── Step 8: Save master table ─────────────────────────
master.to_csv("data/processed/master_satellites.csv", index=False)
print(f"[pipeline] Master table saved: {len(master)} rows")

# ── Step 9: Build subsets for scoring ──────────────────
active = split_active(payloads)
dead = split_dead_in_orbit(payloads)
historical = split_historical_decayed(payloads)
boxscore = build_boxscore(satcat)

# ── Step 10: Save all processed tables ─────────────────
active.to_csv("data/processed/active_satellites.csv", index=False)
dead.to_csv("data/processed/dead_in_orbit.csv", index=False)
historical.to_csv("data/processed/historical_decayed.csv", index=False)
boxscore.to_csv("data/processed/boxscore.csv", index=False)

print("\n✅ Pipeline complete. All tables saved to data/processed/")
print(f"  master_satellites.csv    — {len(master)} rows")
print(f"  active_satellites.csv    — {len(active)} rows")
print(f"  dead_in_orbit.csv        — {len(dead)} rows")
print(f"  historical_decayed.csv   — {len(historical)} rows")
print(f"  boxscore.csv             — {len(boxscore)} rows")