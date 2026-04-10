"""
Diagnostic script — run from project root.
Identifies exactly why assign_historical_labels isn't producing output.
"""

import sys
import os

print("=" * 60)
print("DELPHI LABELER DIAGNOSTIC")
print("=" * 60)

# ── Check 1: Working directory ──────────────────────────────
cwd = os.getcwd()
print(f"\n[1] Working directory: {cwd}")

# ── Check 2: Config import ──────────────────────────────────
print("\n[2] Importing config...")
try:
    from config import DISPOSAL_COMPLIANCE_YEARS
    print(f"    ✅ DISPOSAL_COMPLIANCE_YEARS = {DISPOSAL_COMPLIANCE_YEARS}")
except ImportError as e:
    print(f"    ❌ Import failed: {e}")
    print("    FIX: Make sure config.py is in the project root and contains:")
    print("         DISPOSAL_COMPLIANCE_YEARS = 25")
    print("    FIX: Make sure you're running this script FROM the project root.")
    sys.exit(1)

# ── Check 3: Master CSV exists ──────────────────────────────
master_path = "data/processed/master_satellites.csv"
print(f"\n[3] Looking for {master_path}...")
if os.path.exists(master_path):
    size_mb = os.path.getsize(master_path) / (1024 * 1024)
    print(f"    ✅ Found ({size_mb:.2f} MB)")
else:
    print(f"    ❌ File not found")
    print(f"    Files in data/processed/:")
    processed_dir = "data/processed"
    if os.path.isdir(processed_dir):
        for f in os.listdir(processed_dir):
            print(f"        {f}")
    else:
        print(f"        Directory doesn't exist either")
    sys.exit(1)

# ── Check 4: Load and inspect columns ──────────────────────
import pandas as pd
import numpy as np

print(f"\n[4] Loading master CSV...")
df = pd.read_csv(master_path)
print(f"    Rows: {len(df)}")
print(f"    Columns ({len(df.columns)}):")
for col in sorted(df.columns):
    non_null = df[col].notna().sum()
    pct = non_null / len(df) * 100
    print(f"        {col:40s}  {non_null:>6,} non-null  ({pct:5.1f}%)")

# ── Check 5: Required columns ──────────────────────────────
print(f"\n[5] Checking required columns...")

required = {
    "launch_date": ["launch_date", "Launch_Date", "LAUNCH_DATE", "launch_dt"],
    "decay_date": ["decay_date", "Decay_Date", "DECAY_DATE", "st_decay_date", "decay_dt"],
    "status_code": ["status_code", "status", "Status", "OPS_STATUS_CODE", "ops_status_code"],
    "expected_lifetime_yrs": [
        "expected_lifetime_yrs",
        "Expected_Lifetime",
        "expected_lifetime",
        "exp_lifetime_yrs",
        "Expected_Lifetime_Years",
        "expected_lifetime_years",
        "Expected_Lifetime_(yrs.)",
        "expected_lifetime_(yrs.)",
    ],
}

found_columns = {}
for needed, candidates in required.items():
    match = None
    for c in candidates:
        if c in df.columns:
            match = c
            break
    if match:
        print(f"    ✅ {needed:30s} → found as '{match}'")
        found_columns[needed] = match
    else:
        # Also try case-insensitive partial match
        partial = [c for c in df.columns if needed.split("_")[0].lower() in c.lower()]
        if partial:
            print(f"    ⚠️  {needed:30s} → NOT found by exact name")
            print(f"       Possible matches: {partial}")
        else:
            print(f"    ❌ {needed:30s} → NOT found, no close matches")
        found_columns[needed] = None

# ── Check 6: Status code values ─────────────────────────────
status_col = found_columns.get("status_code")
if status_col:
    print(f"\n[6] Unique values in '{status_col}':")
    vc = df[status_col].value_counts(dropna=False)
    for val, count in vc.items():
        flag = "  ← non-operational" if str(val).strip() in {"-", "D", "NONOP"} else ""
        print(f"        {str(val):20s}  {count:>6,}{flag}")
else:
    print(f"\n[6] SKIPPED — no status column found")

# ── Check 7: Launch date parsing ─────────────────────────────
launch_col = found_columns.get("launch_date")
if launch_col:
    print(f"\n[7] Parsing '{launch_col}'...")
    parsed = pd.to_datetime(df[launch_col], errors="coerce")
    good = parsed.notna().sum()
    bad = parsed.isna().sum()
    original_nulls = df[launch_col].isna().sum()
    print(f"    Parsed OK:  {good:,}")
    print(f"    Failed:     {bad:,}  (of which {original_nulls:,} were already null)")
    print(f"    Sample values: {df[launch_col].dropna().head(3).tolist()}")
else:
    print(f"\n[7] SKIPPED — no launch_date column found")

# ── Check 8: Decay date parsing ──────────────────────────────
decay_col = found_columns.get("decay_date")
if decay_col:
    print(f"\n[8] Parsing '{decay_col}'...")
    parsed = pd.to_datetime(df[decay_col], errors="coerce")
    good = parsed.notna().sum()
    bad = parsed.isna().sum()
    print(f"    Parsed OK:  {good:,}")
    print(f"    Null/NaT:   {bad:,}")
    print(f"    Sample values: {df[decay_col].dropna().head(3).tolist()}")
else:
    print(f"\n[8] SKIPPED — no decay_date column found")

# ── Check 9: Expected lifetime ───────────────────────────────
lifetime_col = found_columns.get("expected_lifetime_yrs")
if lifetime_col:
    print(f"\n[9] Inspecting '{lifetime_col}'...")
    numeric = pd.to_numeric(df[lifetime_col], errors="coerce")
    good = numeric.notna().sum()
    print(f"    Non-null numeric values: {good:,}")
    print(f"    Mean: {numeric.mean():.1f} yrs")
    print(f"    Range: {numeric.min():.1f} – {numeric.max():.1f}")
    print(f"    Sample values: {df[lifetime_col].dropna().head(5).tolist()}")
else:
    print(f"\n[9] SKIPPED — no expected_lifetime_yrs column found")
    print(f"    The labeler will fall back to lifetime=0 (deadline = launch + 25yr)")

# ── Check 10: Attempt labeling ───────────────────────────────
print(f"\n[10] Attempting label assignment...")
print("=" * 60)

try:
    # Remap columns to what the labeler expects
    df_work = df.copy()
    for standard_name, actual_name in found_columns.items():
        if actual_name and actual_name != standard_name:
            print(f"     Renaming '{actual_name}' → '{standard_name}'")
            df_work[standard_name] = df_work[actual_name]

    # Inline the labeling logic to catch exactly where it breaks
    df_work["launch_date"] = pd.to_datetime(df_work["launch_date"], errors="coerce")
    df_work["decay_date"] = pd.to_datetime(df_work.get("decay_date"), errors="coerce")

    if "expected_lifetime_yrs" in df_work.columns:
        df_work["expected_lifetime_yrs"] = pd.to_numeric(
            df_work["expected_lifetime_yrs"], errors="coerce"
        )
    else:
        df_work["expected_lifetime_yrs"] = np.nan

    lifetime_td = pd.to_timedelta(
        df_work["expected_lifetime_yrs"].fillna(0) * 365.25, unit="D"
    )
    df_work["mission_end_date"] = df_work["launch_date"] + lifetime_td

    window = pd.Timedelta(days=DISPOSAL_COMPLIANCE_YEARS * 365.25)
    df_work["compliance_deadline"] = df_work["mission_end_date"] + window

    # Status
    NON_OP = {"-", "D", "NONOP"}
    if "status_code" in df_work.columns:
        df_work["is_inactive"] = (
            df_work["status_code"].astype(str).str.strip().str.upper()
            .isin({c.upper() for c in NON_OP})
        )
    else:
        df_work["is_inactive"] = False

    has_launch = df_work["launch_date"].notna()
    has_decay = df_work["decay_date"].notna()
    has_deadline = df_work["compliance_deadline"].notna()
    now = pd.Timestamp.now()

    print(f"\n     has_launch:   {has_launch.sum():,} / {len(df_work):,}")
    print(f"     has_decay:    {has_decay.sum():,} / {len(df_work):,}")
    print(f"     has_deadline: {has_deadline.sum():,} / {len(df_work):,}")
    print(f"     is_inactive:  {df_work['is_inactive'].sum():,} / {len(df_work):,}")

    df_work["compliance_label"] = "unknown"

    # Rule 1: compliant
    mask_c = has_launch & has_decay & has_deadline & (df_work["decay_date"] <= df_work["compliance_deadline"])
    df_work.loc[mask_c, "compliance_label"] = "compliant"
    print(f"\n     Rule 1 (compliant — decayed in time):    {mask_c.sum():,}")

    # Rule 2: non-compliant (late decay)
    mask_late = has_launch & has_decay & has_deadline & (df_work["decay_date"] > df_work["compliance_deadline"])
    df_work.loc[mask_late, "compliance_label"] = "non_compliant"
    print(f"     Rule 2 (non-compliant — late decay):     {mask_late.sum():,}")

    # Rule 3: non-compliant (dead, past deadline)
    mask_dead = has_launch & ~has_decay & has_deadline & df_work["is_inactive"] & (now > df_work["compliance_deadline"])
    df_work.loc[mask_dead, "compliance_label"] = "non_compliant"
    print(f"     Rule 3 (non-compliant — dead past deadline): {mask_dead.sum():,}")

    # Remaining
    remaining_unknown = (df_work["compliance_label"] == "unknown").sum()
    print(f"     Unknown (remaining):                     {remaining_unknown:,}")

    df_work["is_compliant"] = df_work["compliance_label"] == "compliant"

    # Final distribution
    print(f"\n     ── Final Distribution ──")
    print(df_work["compliance_label"].value_counts().to_string())

    # Save
    out_path = "data/processed/labeled_satellites.csv"
    df_work.to_csv(out_path, index=False)
    print(f"\n     ✅ Saved to {out_path}")
    print(f"     File size: {os.path.getsize(out_path) / (1024*1024):.2f} MB")

except Exception as e:
    print(f"\n     ❌ FAILED at labeling step:")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)