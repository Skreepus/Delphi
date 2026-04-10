import pandas as pd
import numpy as np


def compute_operator_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Builds a reliability score (0-100) for each operator based on their compliance
    and inactive-on-orbit history. Compliance rate carries 60% of the weight,
    inactive ratio carries 30%.

    Returns a DataFrame ranked by reliability_score with one row per operator,
    including compliance_rate, inactive_ratio, reliability_score and reliability_tier.
    """
    agg = df.groupby("operator").agg(
        total=("satellite_name", "count"),
        compliant=("is_compliant", "sum"),
        inactive_on_orbit=("is_inactive", "sum"),
    ).reset_index()

    agg["compliance_rate"] = agg["compliant"] / agg["total"].clip(lower=1)
    agg["inactive_ratio"] = agg["inactive_on_orbit"] / agg["total"].clip(lower=1)

    agg["reliability_score"] = (
        agg["compliance_rate"] * 60 + (1 - agg["inactive_ratio"]) * 30
    ).clip(0, 100).round(1)

    agg["reliability_tier"] = pd.cut(
        agg["reliability_score"],
        bins=[0, 40, 70, 100],
        labels=["low", "medium", "high"],
    )

    return agg.sort_values("reliability_score", ascending=False).reset_index(drop=True)