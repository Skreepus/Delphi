"""
Label Design (v1 — MVP)

FCC rule (adopted Sept 2022): satellites must deorbit within 5 years
of completing their mission.

COMPLIANT:     decayed/deorbited within 5 years of estimated mission end
NON_COMPLIANT: still in orbit or decayed late — exceeded 5-year window
UNKNOWN:       insufficient data, still within compliance window, or
               currently active — excluded from training

Data sources:
    - master_satellites.csv    (UCS+SATCAT+SpaceTrack merged, has expected_lifetime)
    - historical_decayed.csv   (full SATCAT — all decayed payloads)
    - dead_in_orbit.csv        (full SATCAT — dead payloads still in orbit)
    - active_satellites.csv    (full SATCAT — operational payloads, prediction targets)

Strategy:
    1. Label the UCS-matched satellites first (they have expected_lifetime_yrs)
    2. Label the remaining SATCAT-only satellites using lifetime=0 fallback
       (deadline = launch_date + 5 years — conservative)
    3. Active satellites get 'unknown' — they're prediction targets
"""

import pandas as pd
import numpy as np
import os
from config import DISPOSAL_COMPLIANCE_YEARS


_NON_OP_CODES = frozenset({"-", "D", "NONOP"})


def _coerce_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse date columns to datetime."""
    for col in ("launch_date", "decay_date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _add_deadline_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute mission_end_date and compliance_deadline.

    If expected_lifetime_yrs is missing, default to 0.
    This means deadline = launch_date + 5 years (conservative).
    """
    if "expected_lifetime_yrs" not in df.columns:
        df["expected_lifetime_yrs"] = np.nan

    df["expected_lifetime_yrs"] = pd.to_numeric(
        df["expected_lifetime_yrs"], errors="coerce"
    )

    lifetime_days = df["expected_lifetime_yrs"].fillna(0) * 365.25
    df["mission_end_date"] = df["launch_date"] + pd.to_timedelta(lifetime_days, unit="D")

    window = pd.Timedelta(days=DISPOSAL_COMPLIANCE_YEARS * 365.25)
    df["compliance_deadline"] = df["mission_end_date"] + window

    return df


def _resolve_status(df: pd.DataFrame) -> pd.DataFrame:
    """Add is_inactive boolean from status_code column."""
    if "status_code" in df.columns:
        df["is_inactive"] = (
            df["status_code"]
            .astype(str)
            .str.strip()
            .str.upper()
            .isin({c.upper() for c in _NON_OP_CODES})
        )
    elif "status" in df.columns:
        df["is_inactive"] = (
            df["status"]
            .astype(str)
            .str.strip()
            .str.upper()
            .isin({c.upper() for c in _NON_OP_CODES})
        )
    else:
        df["is_inactive"] = False
    return df


def _apply_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign compliance_label based on the 5-year FCC rule.

    Rules:
        1. Decayed within deadline         → compliant
        2. Decayed after deadline           → non_compliant
        3. Dead in orbit, past deadline     → non_compliant
        4. Dead in orbit, within deadline   → unknown (still has time)
        5. Active / operational             → unknown (prediction target)
        6. Missing launch_date              → unknown
    """
    has_launch = df["launch_date"].notna()
    has_decay = df["decay_date"].notna()
    has_deadline = df["compliance_deadline"].notna()
    now = pd.Timestamp.now()

    df["compliance_label"] = "unknown"

    # Rule 1: decayed within compliance window
    mask_compliant = (
        has_launch & has_decay & has_deadline
        & (df["decay_date"] <= df["compliance_deadline"])
    )
    df.loc[mask_compliant, "compliance_label"] = "compliant"

    # Rule 2: decayed but too late
    mask_late_decay = (
        has_launch & has_decay & has_deadline
        & (df["decay_date"] > df["compliance_deadline"])
    )
    df.loc[mask_late_decay, "compliance_label"] = "non_compliant"

    # Rule 3: dead in orbit, past compliance deadline
    mask_dead_past = (
        has_launch
        & ~has_decay
        & has_deadline
        & df["is_inactive"]
        & (now > df["compliance_deadline"])
    )
    df.loc[mask_dead_past, "compliance_label"] = "non_compliant"

    df["is_compliant"] = df["compliance_label"] == "compliant"

    return df


def _enrich_from_master(
    satcat_df: pd.DataFrame,
    master_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Bring expected_lifetime_yrs from the UCS-matched master into
    the full SATCAT rows. Satellites not in UCS keep NaN (fallback to 0).
    """
    if "norad_id" not in satcat_df.columns or "norad_id" not in master_df.columns:
        return satcat_df

    lifetime_lookup = master_df[["norad_id", "expected_lifetime_yrs"]].drop_duplicates(
        subset="norad_id"
    )

    if "expected_lifetime_yrs" in satcat_df.columns:
        satcat_df = satcat_df.drop(columns=["expected_lifetime_yrs"])

    satcat_df = satcat_df.merge(lifetime_lookup, on="norad_id", how="left")
    return satcat_df


def _print_summary(df: pd.DataFrame, name: str) -> None:
    """Print label distribution."""
    counts = df["compliance_label"].value_counts()
    total = len(df)
    print(f"\n── {name} ({total:,} rows) ──")
    for label in ["compliant", "non_compliant", "unknown"]:
        n = counts.get(label, 0)
        pct = n / total * 100 if total else 0
        print(f"  {label:16s}  {n:>7,}  ({pct:5.1f}%)")


def label_all_satellites(
    master_path: str = "data/processed/master_satellites.csv",
    decayed_path: str = "data/processed/historical_decayed.csv",
    dead_path: str = "data/processed/dead_in_orbit.csv",
    active_path: str = "data/processed/active_satellites.csv",
    output_path: str = "data/processed/labeled_satellites.csv",
) -> pd.DataFrame:
    """
    Label all satellites from the full SATCAT splits.

    1. Load decayed, dead-in-orbit, and active splits
    2. Enrich with expected_lifetime_yrs from UCS-matched master
    3. Apply 5-year compliance rule
    4. Combine and save

    Returns the full labeled DataFrame.
    """
    print(f"Compliance window: {DISPOSAL_COMPLIANCE_YEARS} years (FCC rule)")

    # ── Load ────────────────────────────────────────────────────
    master = pd.read_csv(master_path)
    decayed = pd.read_csv(decayed_path)
    dead = pd.read_csv(dead_path)
    active = pd.read_csv(active_path)

    print(f"\nLoaded:")
    print(f"  master (UCS-matched):  {len(master):>7,} rows")
    print(f"  historical_decayed:    {len(decayed):>7,} rows")
    print(f"  dead_in_orbit:         {len(dead):>7,} rows")
    print(f"  active_satellites:     {len(active):>7,} rows")

    # ── Enrich with lifetime from UCS ───────────────────────────
    decayed = _enrich_from_master(decayed, master)
    dead = _enrich_from_master(dead, master)
    active = _enrich_from_master(active, master)

    matched_decayed = decayed["expected_lifetime_yrs"].notna().sum()
    matched_dead = dead["expected_lifetime_yrs"].notna().sum()
    print(f"\nLifetime enrichment (from UCS):")
    print(f"  decayed:  {matched_decayed:,} / {len(decayed):,} have lifetime")
    print(f"  dead:     {matched_dead:,} / {len(dead):,} have lifetime")
    print(f"  (rest use fallback: deadline = launch + {DISPOSAL_COMPLIANCE_YEARS}yr)")

    # ── Process each split ──────────────────────────────────────
    frames = []
    for name, df in [("decayed", decayed), ("dead_in_orbit", dead), ("active", active)]:
        df = _coerce_dates(df)
        df = _add_deadline_columns(df)
        df = _resolve_status(df)
        df = _apply_labels(df)
        df["source_split"] = name
        _print_summary(df, name)
        frames.append(df)

    # ── Combine ─────────────────────────────────────────────────
    labeled = pd.concat(frames, ignore_index=True)

    # Deduplicate — a satellite might appear in master AND a split
    if "norad_id" in labeled.columns:
        before = len(labeled)
        labeled = labeled.drop_duplicates(subset="norad_id", keep="first")
        after = len(labeled)
        if before != after:
            print(f"\nDeduplicated: {before:,} → {after:,} ({before - after:,} duplicates removed)")

    _print_summary(labeled, "FINAL COMBINED")

    # ── Save ────────────────────────────────────────────────────
    labeled.to_csv(output_path, index=False)
    print(f"\n✅ Saved to {output_path}")
    print(f"   File size: {os.path.getsize(output_path) / (1024 * 1024):.2f} MB")

    return labeled


# ── Also keep the single-dataframe version for master-only use ──

def assign_historical_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Label a single DataFrame (e.g. master_satellites.csv).

    For backward compatibility. Prefer label_all_satellites() for
    full coverage across the SATCAT.
    """
    df = df.copy()
    df = _coerce_dates(df)
    df = _add_deadline_columns(df)
    df = _resolve_status(df)
    df = _apply_labels(df)
    _print_summary(df, "master_satellites")
    return df


if __name__ == "__main__":
    label_all_satellites()