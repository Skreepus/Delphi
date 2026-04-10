"""
Tests for scoring functions.
Run with: pytest tests/test_scoring.py
"""
import pytest
import pandas as pd
from src.scoring.satellite_risk import compute_heuristic_risk, assign_risk_tiers
from src.scoring.operator_score import compute_operator_scores


def make_satellite_df():
    return pd.DataFrame({
        "satellite_name": ["SAT-A", "SAT-B", "SAT-C"],
        "operator": ["OpX", "OpX", "OpY"],
        "age_lifetime_ratio": [0.5, 1.8, 3.0],
        "reliability_score": [80.0, 40.0, 20.0],
        "orbit_class": ["LEO", "GEO", "LEO"],
        "is_inactive": [False, True, True],
        "is_compliant": [True, False, False],
    })


def test_heuristic_risk_range():
    df = make_satellite_df()
    scores = compute_heuristic_risk(df)
    assert scores.between(0, 1).all(), "Risk scores must be in [0, 1]"


def test_risk_tiers_labels():
    df = make_satellite_df()
    scores = compute_heuristic_risk(df)
    tiers = assign_risk_tiers(scores)
    assert set(tiers.dropna()).issubset({"LOW", "MEDIUM", "HIGH"})


def test_operator_scores_range():
    df = make_satellite_df()
    result = compute_operator_scores(df)
    assert result["reliability_score"].between(0, 100).all()
