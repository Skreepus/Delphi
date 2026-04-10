"""
Satellite-level disposal risk score: 0.0–1.0 (higher = riskier).
"""
import pandas as pd
import numpy as np


def compute_heuristic_risk(df: pd.DataFrame) -> pd.Series:
    """
    Fallback heuristic risk score when ML model is unavailable or weak.

    Weighted combination of:
        - age/lifetime ratio (overdue satellites score higher)
        - operator reliability (lower operator score → higher satellite risk)
        - orbit class (LEO penalised less than GEO per ITU rules)
    """
    score = pd.Series(0.0, index=df.index)

    # Age/lifetime ratio contribution
    if "age_lifetime_ratio" in df.columns:
        score += df["age_lifetime_ratio"].clip(0, 3).fillna(1) / 3 * 0.5

    # Operator reliability contribution (inverted)
    if "reliability_score" in df.columns:
        score += (1 - df["reliability_score"].fillna(50) / 100) * 0.3

    # Orbit class contribution (placeholder)
    if "orbit_class" in df.columns:
        geo_mask = df["orbit_class"].str.upper().eq("GEO")
        score += geo_mask.astype(float) * 0.2

    return score.clip(0, 1).rename("risk_score")


def assign_risk_tiers(risk_scores: pd.Series) -> pd.Series:
    """Map continuous risk score to LOW / MEDIUM / HIGH tier."""
    from config import RISK_HIGH_THRESHOLD, RISK_MEDIUM_THRESHOLD
    return pd.cut(
        risk_scores,
        bins=[0, RISK_MEDIUM_THRESHOLD, RISK_HIGH_THRESHOLD, 1.0],
        labels=["LOW", "MEDIUM", "HIGH"],
        include_lowest=True,
    ).rename("risk_tier")
