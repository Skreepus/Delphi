import pandas as pd
import numpy as np
from config import RISK_HIGH_THRESHOLD, RISK_MEDIUM_THRESHOLD


def compute_heuristic_risk(df: pd.DataFrame) -> pd.Series:
    """
    Scores each satellite's disposal risk (0-1) using three weighted factors:
    age/lifetime ratio (50%), operator reliability (30%), and GEO orbit (20%).
    Returns a Series named 'risk_score'.
    """

    score = pd.Series(0.0, index=df.index)

    if "age_lifetime_ratio" in df.columns:
        score += df["age_lifetime_ratio"].clip(0, 3).fillna(1) / 3 * 0.5

    if "reliability_score" in df.columns:
        score += (1 - df["reliability_score"].fillna(50) / 100) * 0.3

    if "orbit_class" in df.columns:
        score += df["orbit_class"].str.upper().eq("GEO").astype(float) * 0.2

    return score.clip(0, 1).rename("risk_score")


def assign_risk_tiers(risk_scores: pd.Series) -> pd.Series:
    """
    Buckets risk scores into LOW, MEDIUM or HIGH tiers using thresholds
    defined in config. Returns a Series named 'risk_tier'.
    """
    return pd.cut(
        risk_scores,
        bins=[0, RISK_MEDIUM_THRESHOLD, RISK_HIGH_THRESHOLD, 1.0],
        labels=["LOW", "MEDIUM", "HIGH"],
        include_lowest=True,
    ).rename("risk_tier")