"""
Operator Reliability Score (v1 — MVP)

For each operator, calculate the fraction of their historical satellites
that were disposed of within the FCC 5-year compliance window.

Score range: 0.0 (worst) to 1.0 (best)
    1.0 = every historical satellite was compliant
    0.0 = no historical satellite was compliant

Operators with fewer than MIN_HISTORY satellites get a penalised
score to avoid inflated ratings from thin data.

Output: one row per operator with reliability score and supporting counts.
"""

import pandas as pd
import numpy as np
import os


# Minimum historical satellites needed for a confident score.
# Operators below this threshold get pulled toward the global average.
MIN_HISTORY = 3


def compute_operator_reliability(
    labeled_path: str = "data/processed/labeled_satellites.csv",
    output_path: str = "data/processed/operator_reliability.csv",
) -> pd.DataFrame:
    """
    Build operator reliability scores from labeled satellite data.

    Returns DataFrame with one row per operator.
    """
    df = pd.read_csv(labeled_path)

    # ── Filter to training rows only (ignore unknowns) ──────────
    historical = df[df["compliance_label"].isin(["compliant", "non_compliant"])].copy()

    print(f"Historical satellites with labels: {len(historical):,}")

    # ── Pick the best operator column available ─────────────────
    if "operator_resolved" in historical.columns:
        op_col = "operator_resolved"
    elif "operator_clean" in historical.columns:
        op_col = "operator_clean"
    elif "operator" in historical.columns:
        op_col = "operator"
    elif "owner_code" in historical.columns:
        op_col = "owner_code"
    else:
        raise ValueError("No operator column found in labeled data")

    print(f"Grouping by: '{op_col}'")

    # ── Aggregate per operator ──────────────────────────────────
    agg = (
        historical
        .groupby(op_col)
        .agg(
            total_historical=("compliance_label", "count"),
            compliant_count=("is_compliant", "sum"),
        )
        .reset_index()
        .rename(columns={op_col: "operator"})
    )

    agg["non_compliant_count"] = agg["total_historical"] - agg["compliant_count"]
    agg["raw_reliability"] = agg["compliant_count"] / agg["total_historical"]

    # ── Bayesian smoothing for thin histories ───────────────────
    # Pull operators with few satellites toward the global average
    # so a 1/1 operator doesn't get a perfect 1.0
    global_rate = historical["is_compliant"].mean()
    print(f"Global compliance rate: {global_rate:.3f}")

    agg["reliability_score"] = (
        (agg["compliant_count"] + MIN_HISTORY * global_rate)
        / (agg["total_historical"] + MIN_HISTORY)
    )

    # ── Confidence flag ─────────────────────────────────────────
    agg["confidence"] = np.where(
        agg["total_historical"] >= 10, "high",
        np.where(agg["total_historical"] >= MIN_HISTORY, "medium", "low")
    )

    # ── Sort worst operators first ──────────────────────────────
    agg = agg.sort_values("reliability_score", ascending=True).reset_index(drop=True)

    # ── Summary ─────────────────────────────────────────────────
    print(f"\nOperators scored: {len(agg):,}")
    print(f"\n── Reliability Distribution ──")
    print(f"  Mean:   {agg['reliability_score'].mean():.3f}")
    print(f"  Median: {agg['reliability_score'].median():.3f}")
    print(f"  Min:    {agg['reliability_score'].min():.3f}")
    print(f"  Max:    {agg['reliability_score'].max():.3f}")

    print(f"\n── Worst 10 Operators ──")
    worst = agg.head(10)[["operator", "total_historical", "compliant_count",
                           "non_compliant_count", "reliability_score", "confidence"]]
    print(worst.to_string(index=False))

    print(f"\n── Best 10 Operators ──")
    best = agg.tail(10)[["operator", "total_historical", "compliant_count",
                          "non_compliant_count", "reliability_score", "confidence"]]
    print(best.to_string(index=False))

    # ── Save ────────────────────────────────────────────────────
    agg.to_csv(output_path, index=False)
    print(f"\n✅ Saved to {output_path}")
    print(f"   {len(agg)} operators scored")

    return agg


if __name__ == "__main__":
    compute_operator_reliability()