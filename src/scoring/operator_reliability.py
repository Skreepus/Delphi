"""
Operator Reliability Score (v1 — MVP)

Composite score per OPERATOR (company-level, not country-level).

Components:
    compliance_component = bayesian_smoothed_compliance_rate × COMPLIANCE_WEIGHT
    debris_component     = (1 - inactive_ratio) × DEBRIS_WEIGHT
    reliability_score    = compliance_component + debris_component  (0–100)

For UCS-matched satellites:  grouped by operator name (SpaceX, ISRO, etc.)
For SATCAT-only satellites:  grouped by owner_code (US, CIS, PRC)
    → These are flagged as operator_source = "satcat_owner_code"

Score range: 0 (worst) to 100 (best)

Tiers (from config):
    high:   score >= 70
    medium: score >= 40
    low:    score <  40

Bayesian smoothing:
    Operators with fewer than MIN_OPERATOR_HISTORY satellites get pulled
    toward the global average compliance rate to prevent extreme scores
    from thin data.

    Formula:
        smoothed_rate = (compliant + m × g) / (total + m)
    Where:
        m = MIN_OPERATOR_HISTORY (smoothing strength)
        g = global compliance rate across all operators
"""

import pandas as pd
import numpy as np
import os

from config import (
    LABELED_CSV,
    OPERATOR_SCORES_CSV,
    COMPLIANCE_WEIGHT,
    DEBRIS_WEIGHT,
    RELIABILITY_TIERS,
)

try:
    from config import MIN_OPERATOR_HISTORY
except ImportError:
    MIN_OPERATOR_HISTORY = 3


# ════════════════════════════════════════════════════════════════
# Operator Column Resolution
# ════════════════════════════════════════════════════════════════


def _build_operator_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a single 'operator_final' column using best available name.

    Priority (best first — first match wins):
        1. operator_resolved  → "spacex"         (from UCS fuzzy matching)
        2. operator_clean     → "spacex"         (from UCS normalised)
        3. operator           → "SpaceX"         (from UCS raw)
        4. owner_code         → "US"             (from SATCAT — last resort)

    Also adds:
        operator_source:  "ucs_operator" or "satcat_owner_code"
        operator_display: title-cased version for UI display
    """
    df = df.copy()
    df["operator_final"] = np.nan

    # ── Fill best-first. Each column only fills remaining NaN. ──
    for col in ("operator_resolved", "operator_clean", "operator", "owner_code"):
        if col in df.columns:
            mask = df["operator_final"].isna() & df[col].notna()
            df.loc[mask, "operator_final"] = df.loc[mask, col]

    # ── Clean up values ─────────────────────────────────────────
    df["operator_final"] = (
        df["operator_final"]
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({"nan": np.nan, "": np.nan})
    )

    # ── Track where the name came from ──────────────────────────
    if "operator_resolved" in df.columns:
        df["operator_source"] = np.where(
            df["operator_resolved"].notna(),
            "ucs_operator",
            "satcat_owner_code"
        )
    else:
        df["operator_source"] = "satcat_owner_code"

    # ── Summary ─────────────────────────────────────────────────
    ucs_count = (df["operator_source"] == "ucs_operator").sum()
    satcat_count = (df["operator_source"] == "satcat_owner_code").sum()
    unique_ops = df["operator_final"].nunique()

    print(f"\n── Operator Resolution ──")
    print(f"  Named operators (UCS):     {ucs_count:,}")
    print(f"  Country codes (SATCAT):    {satcat_count:,}")
    print(f"  Unique operators/codes:    {unique_ops:,}")

    # ── Show sample to verify correct resolution ────────────────
    if "operator_resolved" in df.columns:
        sample_ucs = (
            df[df["operator_resolved"].notna()]
            [["operator_resolved", "owner_code", "operator_final"]]
            .drop_duplicates(subset="operator_final")
            .head(10)
        )
        if len(sample_ucs) > 0:
            print(f"\n  Sample UCS-matched operators:")
            print(f"  {'operator_resolved':30s}  {'owner_code':12s}  {'operator_final':30s}")
            for _, row in sample_ucs.iterrows():
                print(
                    f"  {str(row['operator_resolved']):30s}  "
                    f"{str(row['owner_code']):12s}  "
                    f"{str(row['operator_final']):30s}"
                )

    return df


# ════════════════════════════════════════════════════════════════
# Summary Printing
# ════════════════════════════════════════════════════════════════


def _print_summary(agg: pd.DataFrame, global_rate: float) -> None:
    """Print scoring summary to stdout."""
    print(f"\n{'=' * 70}")
    print(f"OPERATOR RELIABILITY SCORING COMPLETE")
    print(f"{'=' * 70}")
    print(f"\nGlobal compliance rate: {global_rate:.3f}")
    print(f"Bayesian smoothing (m): {MIN_OPERATOR_HISTORY}")
    print(f"Weights: compliance={COMPLIANCE_WEIGHT}%, debris={DEBRIS_WEIGHT}%")
    print(f"Operators scored: {len(agg):,}")

    # ── Score distribution ──────────────────────────────────────
    print(f"\n── Score Distribution ──")
    print(f"  Mean:   {agg['reliability_score'].mean():.1f}")
    print(f"  Median: {agg['reliability_score'].median():.1f}")
    print(f"  Min:    {agg['reliability_score'].min():.1f}")
    print(f"  Max:    {agg['reliability_score'].max():.1f}")

    # ── Tier counts ─────────────────────────────────────────────
    print(f"\n── Tier Counts ──")
    counts = agg["reliability_tier"].value_counts()
    for tier in ["high", "medium", "low"]:
        n = counts.get(tier, 0)
        pct = n / len(agg) * 100
        print(f"  {tier:8s}  {n:>5,}  ({pct:5.1f}%)")

    # ── Display columns ─────────────────────────────────────────
    display_cols = [
        "operator", "operator_display", "operator_source",
        "total_historical", "compliant_count", "non_compliant_count",
        "inactive_on_orbit", "reliability_score", "reliability_tier",
        "confidence",
    ]
    display_cols = [c for c in display_cols if c in agg.columns]

    # ── Split named operators vs country codes ──────────────────
    named = agg[agg["operator_source"] == "ucs_operator"]
    country = agg[agg["operator_source"] == "satcat_owner_code"]

    if len(named) > 0:
        # Worst named (companies)
        worst_named = named.head(15)
        print(f"\n── 15 Worst Named Operators (companies) ──")
        print(worst_named[display_cols].to_string(index=False))

        # Best named (companies)
        best_named = named.tail(15)
        print(f"\n── 15 Best Named Operators (companies) ──")
        print(best_named[display_cols].to_string(index=False))

    if len(country) > 0:
        # Country-level
        print(f"\n── Country-Level Scores (SATCAT-only satellites) ──")
        print(country[display_cols].to_string(index=False))


# ════════════════════════════════════════════════════════════════
# Core Scoring Logic
# ════════════════════════════════════════════════════════════════


def compute_operator_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a composite reliability score (0–100) for each operator.

    Steps:
        1. Build unified operator column (company names where available)
        2. Compute Bayesian-smoothed compliance rate from labeled history
        3. Compute inactive-in-orbit ratio from all tracked objects
        4. Combine into weighted composite score
        5. Assign tiers and confidence flags

    Parameters
    ----------
    df : pd.DataFrame
        Full labeled satellite table from labeled_satellites.csv.
        Must contain compliance_label, is_compliant, and at least
        one operator column.

    Returns
    -------
    pd.DataFrame
        One row per operator, sorted worst-first by reliability_score.
    """
    # ── Build unified operator column ───────────────────────────
    df = _build_operator_column(df)
    op_col = "operator_final"

    # Drop rows with no operator identity at all
    missing_op = df[op_col].isna().sum()
    if missing_op > 0:
        print(f"  Dropping {missing_op:,} rows with no operator identity")
        df = df[df[op_col].notna()].copy()

    # ════════════════════════════════════════════════════════════
    # PART 1: Compliance aggregation (from labeled history only)
    # ════════════════════════════════════════════════════════════

    historical = df[
        df["compliance_label"].isin(["compliant", "non_compliant"])
    ].copy()
    print(f"\nHistorical satellites with labels: {len(historical):,}")

    compliance_agg = (
        historical
        .groupby(op_col)
        .agg(
            total_historical=("compliance_label", "count"),
            compliant_count=("is_compliant", "sum"),
        )
        .reset_index()
        .rename(columns={op_col: "operator"})
    )

    compliance_agg["non_compliant_count"] = (
        compliance_agg["total_historical"] - compliance_agg["compliant_count"]
    )
    compliance_agg["raw_compliance_rate"] = (
        compliance_agg["compliant_count"]
        / compliance_agg["total_historical"]
    )

    # ── Bayesian smoothing ──────────────────────────────────────
    global_rate = historical["is_compliant"].mean()

    compliance_agg["compliance_rate_smoothed"] = (
        (compliance_agg["compliant_count"] + MIN_OPERATOR_HISTORY * global_rate)
        / (compliance_agg["total_historical"] + MIN_OPERATOR_HISTORY)
    )

    # ════════════════════════════════════════════════════════════
    # PART 2: Inactive/debris aggregation (from ALL satellites)
    # ════════════════════════════════════════════════════════════

    all_sats = df.copy()

    # Ensure is_inactive flag exists
    if "is_inactive" not in all_sats.columns:
        if "status_code" in all_sats.columns:
            all_sats["is_inactive"] = (
                all_sats["status_code"]
                .astype(str)
                .str.strip()
                .str.upper()
                .isin({"-", "D", "NONOP"})
            )
        else:
            all_sats["is_inactive"] = False

    # Still in orbit = no decay date
    if "decay_date" in all_sats.columns:
        all_sats["_still_in_orbit"] = pd.to_datetime(
            all_sats["decay_date"], errors="coerce"
        ).isna()
    else:
        all_sats["_still_in_orbit"] = True

    # Inactive AND still in orbit = space junk
    all_sats["_inactive_in_orbit"] = (
        all_sats["is_inactive"] & all_sats["_still_in_orbit"]
    )

    debris_agg = (
        all_sats
        .groupby(op_col)
        .agg(
            total_objects=("is_inactive", "count"),
            inactive_on_orbit=("_inactive_in_orbit", "sum"),
        )
        .reset_index()
        .rename(columns={op_col: "operator"})
    )

    debris_agg["inactive_ratio"] = (
        debris_agg["inactive_on_orbit"]
        / debris_agg["total_objects"].clip(lower=1)
    )

    # ════════════════════════════════════════════════════════════
    # PART 3: Capture operator source for each operator
    # ════════════════════════════════════════════════════════════

    source_map = (
        df.groupby(op_col)["operator_source"]
        .first()
        .reset_index()
        .rename(columns={op_col: "operator"})
    )

    # ════════════════════════════════════════════════════════════
    # PART 4: Merge everything
    # ════════════════════════════════════════════════════════════

    agg = compliance_agg.merge(debris_agg, on="operator", how="outer")
    agg = agg.merge(source_map, on="operator", how="left")

    # Fill NaN for operators that appear in one aggregation but not the other
    agg["compliance_rate_smoothed"] = agg["compliance_rate_smoothed"].fillna(
        global_rate
    )
    agg["raw_compliance_rate"] = agg["raw_compliance_rate"].fillna(0.0)
    agg["inactive_ratio"] = agg["inactive_ratio"].fillna(0.5)
    agg["total_historical"] = agg["total_historical"].fillna(0).astype(int)
    agg["compliant_count"] = agg["compliant_count"].fillna(0).astype(int)
    agg["non_compliant_count"] = agg["non_compliant_count"].fillna(0).astype(int)
    agg["inactive_on_orbit"] = agg["inactive_on_orbit"].fillna(0).astype(int)
    agg["total_objects"] = agg["total_objects"].fillna(0).astype(int)
    agg["operator_source"] = agg["operator_source"].fillna("satcat_owner_code")

    # ════════════════════════════════════════════════════════════
    # PART 5: Composite score (0–100)
    # ════════════════════════════════════════════════════════════

    # compliance_component: higher compliance rate → higher score
    # debris_component:     lower inactive ratio → higher score
    agg["compliance_component"] = (
        agg["compliance_rate_smoothed"] * COMPLIANCE_WEIGHT
    )
    agg["debris_component"] = (
        (1 - agg["inactive_ratio"]) * DEBRIS_WEIGHT
    )

    agg["reliability_score"] = (
        agg["compliance_component"] + agg["debris_component"]
    ).clip(0, 100).round(1)

    # ════════════════════════════════════════════════════════════
    # PART 6: Confidence flag
    # ════════════════════════════════════════════════════════════

    agg["confidence"] = np.where(
        agg["total_historical"] >= 10, "high",
        np.where(
            agg["total_historical"] >= MIN_OPERATOR_HISTORY,
            "medium",
            "low"
        )
    )

    # ════════════════════════════════════════════════════════════
    # PART 7: Reliability tier
    # ════════════════════════════════════════════════════════════

    tier_high = RELIABILITY_TIERS.get("high", 70)
    tier_medium = RELIABILITY_TIERS.get("medium", 40)

    agg["reliability_tier"] = np.where(
        agg["reliability_score"] >= tier_high, "high",
        np.where(
            agg["reliability_score"] >= tier_medium,
            "medium",
            "low"
        )
    )

    # ════════════════════════════════════════════════════════════
    # PART 8: Display name
    # ════════════════════════════════════════════════════════════

    agg["operator_display"] = agg["operator"].str.title()

    # ════════════════════════════════════════════════════════════
    # PART 9: Sort and print
    # ════════════════════════════════════════════════════════════

    agg = agg.sort_values(
        "reliability_score", ascending=True
    ).reset_index(drop=True)

    _print_summary(agg, global_rate)

    return agg


# ════════════════════════════════════════════════════════════════
# Entry Point
# ════════════════════════════════════════════════════════════════


def compute_operator_reliability(
    labeled_path=LABELED_CSV,
    output_path=OPERATOR_SCORES_CSV,
) -> pd.DataFrame:
    """
    Load labeled satellites, compute per-operator scores, save output.

    Parameters
    ----------
    labeled_path : str or Path
        Path to labeled_satellites.csv
    output_path : str or Path
        Path to write operator_scores.csv

    Returns
    -------
    pd.DataFrame
        One row per operator with reliability scores and metadata.
    """
    print(f"Loading: {labeled_path}")
    df = pd.read_csv(labeled_path, low_memory=False)

    scored = compute_operator_scores(df)

    scored.to_csv(output_path, index=False)
    print(f"\n✅ Saved to {output_path}")
    print(f"   {len(scored)} operators scored")

    return scored


if __name__ == "__main__":
    compute_operator_reliability()