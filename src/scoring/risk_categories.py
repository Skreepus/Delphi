"""
risk_categories.py  —  Simplified for second-year students

WHAT THIS FILE DOES
-------------------
Computes a heuristic (rule-based) risk score for each satellite and
maps it to a LOW / MEDIUM / HIGH tier. This runs before or instead
of the ML model, and can act as a sanity check on ML outputs.

Two levels of scoring:
    1. OPERATOR-LEVEL: categorise each operator as low / medium / high
       risk based on their reliability score (0–100).
    2. SATELLITE-LEVEL: compute a 0–1 risk score for each satellite
       using a weighted combination of three factors.

THE HEURISTIC RISK FORMULA
---------------------------
    risk = 0.5 * age_factor
           + 0.3 * operator_factor
           + 0.2 * geo_factor

Each factor is between 0 and 1, so the total is also between 0 and 1.
The weights (0.5, 0.3, 0.2) are domain-driven choices — satellites past
their design life are the biggest driver of non-compliance, followed by
operator reliability, then orbit type.

    age_factor      = min(age_lifetime_ratio, 3) / 3
                      age_lifetime_ratio = age_years / expected_lifetime_yrs
                      Cap at 3 so a satellite that is 10x overdue doesn't
                      produce a wildly inflated factor — we already know it's
                      high risk if it's just 2x overdue.
                      Missing → assume 1.0 (at end of life, moderate risk).

    operator_factor = 1 - (reliability_score / 100)
                      reliability_score is 0–100 (higher = better operator).
                      We invert it: poor operator → factor close to 1 → high risk.
                      Missing → assume 0.5 (average risk).

    geo_factor      = 1 if orbit_class == "GEO", else 0
                      GEO satellites (≈35,786 km) experience essentially no
                      atmospheric drag, so they will stay in orbit for thousands
                      of years unless actively moved. This makes disposal
                      obligations particularly important for GEO operators.

RISK TIERS
----------
    final_risk < 0.4  → LOW
    0.4 ≤ risk < 0.7  → MEDIUM
    risk ≥ 0.7        → HIGH
"""

import pandas as pd
import numpy as np
import os

from config import (
    RISK_HIGH_THRESHOLD,
    RISK_MEDIUM_THRESHOLD,
    RELIABILITY_TIERS,
    OPERATOR_SCORES_CSV,
    LABELED_CSV,
    SATELLITE_RISK_CSV,
)


# ============================================================
# assign_operator_risk
# ============================================================

def assign_operator_risk(
    df: pd.DataFrame,
    score_col: str = "reliability_score",
) -> pd.DataFrame:
    """
    Add a risk_category column to the operator scores table.

    Applies simple threshold rules to the reliability score (0–100):
        score >= 70  →  "low"    (trustworthy operator)
        score >= 40  →  "medium"
        score <  40  →  "high"   (history of non-compliance)

    np.where(condition, value_if_true, value_if_false) is equivalent to:
        if condition: value_if_true else value_if_false
    Nested np.where calls handle three cases.

    Parameters
    ----------
    df        : operator scores table (one row per operator)
    score_col : name of the column containing the 0–100 score

    Returns
    -------
    pd.DataFrame — copy of input with risk_category column added
    """
    df = df.copy()

    tier_high   = RELIABILITY_TIERS.get("high",   70)
    tier_medium = RELIABILITY_TIERS.get("medium", 40)

    df["risk_category"] = np.where(
        df[score_col] >= tier_high,   "low",
        np.where(
            df[score_col] >= tier_medium, "medium", "high"
        )
    )

    counts = df["risk_category"].value_counts()
    print("── Operator Risk Categories ──")
    for cat in ["high", "medium", "low"]:
        n   = counts.get(cat, 0)
        pct = n / len(df) * 100 if len(df) > 0 else 0
        print(f"  {cat:8s}  {n:>5,}  ({pct:5.1f}%)")

    return df


# ============================================================
# compute_heuristic_risk
# ============================================================

def compute_heuristic_risk(df: pd.DataFrame) -> pd.Series:
    """
    Compute a 0–1 disposal risk score for each satellite.

    FORMULA (see module docstring for full explanation):
        risk = 0.5 * age_factor
               + 0.3 * operator_factor
               + 0.2 * geo_factor

    FACTOR DETAILS:

    age_factor (weight 0.5):
        age_lifetime_ratio capped at 3, divided by 3 → maps [0, 3] to [0, 1].
        clip(0, 3):   values below 0 become 0, values above 3 become 3.
        fillna(1.0):  if ratio is unknown, assume "at end of life" (ratio = 1)
                      → age_factor = 1/3 ≈ 0.33, a moderate-risk assumption.

    operator_factor (weight 0.3):
        reliability_score is 0–100 where 100 = perfectly reliable.
        1 - score/100 inverts it: score=100 → factor=0.0, score=0 → factor=1.0.
        fillna(50): unknown operators assumed to be average.

    geo_factor (weight 0.2):
        eq("GEO") returns a boolean Series; astype(float) converts True→1, False→0.

    Parameters
    ----------
    df : DataFrame with optional columns:
         age_lifetime_ratio, reliability_score, orbit_class

    Returns
    -------
    pd.Series of float, values in [0, 1], named "risk_score"
    """
    score = pd.Series(0.0, index=df.index)

    # ── Factor 1: Age / Lifetime ratio (50%) ────────────────────
    if "age_lifetime_ratio" in df.columns:
        age_factor = df["age_lifetime_ratio"].clip(0, 3).fillna(1.0) / 3.0
        score += age_factor * 0.5
    else:
        score += 0.5 * 0.5   # no lifetime data → assume moderate risk

    # ── Factor 2: Operator reliability (30%) ────────────────────
    if "reliability_score" in df.columns:
        operator_factor = 1.0 - df["reliability_score"].fillna(50) / 100.0
        score += operator_factor * 0.3
    else:
        score += 0.5 * 0.3   # no operator data → assume average risk

    # ── Factor 3: GEO orbit penalty (20%) ───────────────────────
    if "orbit_class" in df.columns:
        is_geo = df["orbit_class"].astype(str).str.upper().eq("GEO").astype(float)
        score += is_geo * 0.2
    # else: no orbit data → no penalty added (conservative)

    return score.clip(0, 1).rename("risk_score")


# ============================================================
# assign_risk_tiers
# ============================================================

def assign_risk_tiers(risk_scores: pd.Series) -> pd.Series:
    """
    Convert continuous risk scores into LOW / MEDIUM / HIGH labels.

    pd.cut(values, bins, labels) partitions values into intervals:
        bins=[0, 0.4, 0.7, 1.0]  defines three intervals:
            [0,   0.4]  → "LOW"
            (0.4, 0.7]  → "MEDIUM"
            (0.7, 1.0]  → "HIGH"
        include_lowest=True makes the left edge of the first bin inclusive
        (so a score of exactly 0.0 gets "LOW" rather than NaN).

    Parameters
    ----------
    risk_scores : pd.Series of float in [0, 1]

    Returns
    -------
    pd.Series of category labels, named "risk_tier"
    """
    return pd.cut(
        risk_scores,
        bins=[0, RISK_MEDIUM_THRESHOLD, RISK_HIGH_THRESHOLD, 1.0],
        labels=["LOW", "MEDIUM", "HIGH"],
        include_lowest=True,
    ).rename("risk_tier")


# ============================================================
# _build_operator_final  —  helper for operator name resolution
# ============================================================

def _build_operator_final(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a unified operator_final column for joining.

    Priority (best first):
        1. operator_resolved  → "spacex"
        2. operator_clean     → "spacex"
        3. operator           → "SpaceX"
        4. owner_code         → "US"  (last resort)

    Initialises as string dtype to avoid the FutureWarning about
    setting string values into a float64 column.
    """
    # Initialise as empty string column (not NaN float)
    df["operator_final"] = pd.Series("", dtype="string", index=df.index)
    df["operator_final"] = pd.NA  # string-typed NA, not float NaN

    for col in ("operator_resolved", "operator_clean", "operator", "owner_code"):
        if col in df.columns:
            mask = df["operator_final"].isna() & df[col].notna()
            df.loc[mask, "operator_final"] = df.loc[mask, col].astype(str)

    df["operator_final"] = (
        df["operator_final"]
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({"nan": np.nan, "<na>": np.nan, "": np.nan})
    )

    return df


# ============================================================
# compute_satellite_risk  —  full pipeline
# ============================================================

def compute_satellite_risk(
    labeled_path=LABELED_CSV,
    operator_scores_path=OPERATOR_SCORES_CSV,
    output_path=SATELLITE_RISK_CSV,
) -> pd.DataFrame:
    """
    End-to-end heuristic risk scoring for all satellites.

    STEPS:
        1. Load satellite + operator data
        2. Resolve operator name → normalised join key
        3. Left-join operator reliability score onto each satellite
        4. Compute age_years and age_lifetime_ratio
        5. Compute heuristic risk score via compute_heuristic_risk()
        6. Assign LOW / MEDIUM / HIGH tiers via assign_risk_tiers()
        7. Print summary and top-15 highest-risk active satellites
        8. Save to CSV

    Returns
    -------
    pd.DataFrame with risk_score and risk_tier columns added
    """
    print("Loading satellite data...")
    sats = pd.read_csv(labeled_path, low_memory=False)
    print(f"  Satellites: {len(sats):,}")

    print("Loading operator scores...")
    ops = pd.read_csv(operator_scores_path)
    print(f"  Operators: {len(ops):,}")

    # ── Resolve operator name ────────────────────────────────────
    sats = _build_operator_final(sats)

    # ── Join reliability score onto each satellite ───────────────
    op_lookup = ops[["operator", "reliability_score"]].rename(
        columns={"operator": "operator_final"}
    )

    # Drop reliability_score if it already exists to avoid _x/_y
    if "reliability_score" in sats.columns:
        sats = sats.drop(columns=["reliability_score"])

    sats = sats.merge(op_lookup, on="operator_final", how="left")

    matched = sats["reliability_score"].notna().sum()
    print(f"  Operator scores joined: {matched:,} / {len(sats):,}")

    # ── Compute age and age/lifetime ratio ───────────────────────
    if "launch_date" in sats.columns:
        sats["launch_date"] = pd.to_datetime(sats["launch_date"], errors="coerce")
        sats["age_years"] = (
            (pd.Timestamp.now() - sats["launch_date"]).dt.days / 365.25
        )
    else:
        sats["age_years"] = np.nan

    if "expected_lifetime_yrs" in sats.columns:
        sats["expected_lifetime_yrs"] = pd.to_numeric(
            sats["expected_lifetime_yrs"], errors="coerce"
        )
        # clip(lower=0.1) prevents divide-by-zero for satellites with a
        # listed lifetime of 0; 0.1 is small enough to still flag very old sats
        sats["age_lifetime_ratio"] = (
            sats["age_years"] / sats["expected_lifetime_yrs"].clip(lower=0.1)
        )
    else:
        sats["age_lifetime_ratio"] = np.nan

    # ── Score and tier ───────────────────────────────────────────
    sats["risk_score"] = compute_heuristic_risk(sats)
    sats["risk_tier"]  = assign_risk_tiers(sats["risk_score"])

    # ── Summary ──────────────────────────────────────────────────
    print(f"\n── Satellite Risk Distribution ──")
    print(f"  Mean:   {sats['risk_score'].mean():.3f}")
    print(f"  Median: {sats['risk_score'].median():.3f}")

    tier_counts = sats["risk_tier"].value_counts()
    for tier in ["HIGH", "MEDIUM", "LOW"]:
        n   = tier_counts.get(tier, 0)
        pct = n / len(sats) * 100
        print(f"  {tier:8s}  {n:>7,}  ({pct:5.1f}%)")

    # Show top 15 highest-risk active (unknown-label) satellites
    active = sats[sats["compliance_label"] == "unknown"].copy()
    if len(active) > 0:
        worst_active  = active.nlargest(15, "risk_score")
        display_cols  = [
            "norad_id", "satellite_name", "operator_final",
            "orbit_class", "age_years", "age_lifetime_ratio",
            "reliability_score", "risk_score", "risk_tier",
        ]
        display_cols = [c for c in display_cols if c in worst_active.columns]
        print(f"\n── 15 Highest Risk Active Satellites ──")
        print(worst_active[display_cols].to_string(index=False))

    # ── Save ─────────────────────────────────────────────────────
    output_dir = os.path.dirname(str(output_path))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    sats.to_csv(output_path, index=False)
    print(f"\n✅ Saved to {output_path}")
    print(f"   {len(sats):,} satellites scored")

    return sats


# ============================================================
# Entry Points
# ============================================================

def run_operator_risk():
    """Add risk categories to operator scores file."""
    print("Adding risk categories to operator scores...")
    ops = pd.read_csv(OPERATOR_SCORES_CSV)
    ops = assign_operator_risk(ops)
    ops.to_csv(OPERATOR_SCORES_CSV, index=False)
    print(f"\n✅ Updated {OPERATOR_SCORES_CSV}")


def run_satellite_risk():
    """Compute satellite-level risk scores."""
    compute_satellite_risk()


if __name__ == "__main__":
    run_satellite_risk()