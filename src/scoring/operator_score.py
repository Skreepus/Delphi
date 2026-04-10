"""
Operator reliability score: 0–100 (higher = more reliable).
"""
import pandas as pd
import numpy as np


def compute_operator_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute an operator reliability score from aggregated satellite data.

    Formula (v1 heuristic — replace with model output if available):
        score = compliance_rate * 60
              + (1 - inactive_ratio) * 30
              + recency_bonus * 10

    Returns:
        DataFrame with one row per operator and a 'reliability_score' column.
    """
    agg = df.groupby("operator").agg(
        total=("satellite_name", "count"),
        compliant=("is_compliant", "sum"),
        inactive_on_orbit=("is_inactive", "sum"),
    ).reset_index()

    agg["compliance_rate"] = agg["compliant"] / agg["total"].clip(lower=1)
    agg["inactive_ratio"] = agg["inactive_on_orbit"] / agg["total"].clip(lower=1)

    agg["reliability_score"] = (
        agg["compliance_rate"] * 60
        + (1 - agg["inactive_ratio"]) * 30
    ).clip(0, 100).round(1)

    agg["reliability_tier"] = pd.cut(
        agg["reliability_score"],
        bins=[0, 40, 70, 100],
        labels=["low", "medium", "high"],
    )

    return agg.sort_values("reliability_score", ascending=False).reset_index(drop=True)
