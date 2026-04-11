"""
Tests for feature engineering.
"""
import pandas as pd
from src.features.feature_engineering import add_temporal_features


def test_satellite_age_non_negative():
    df = pd.DataFrame({"launch_date": ["2010-01-01", "2020-06-15", None], "expected_lifetime_yrs": [10, 7, 5]})
    result = add_temporal_features(df)
    assert (result["satellite_age_yrs"].dropna() >= 0).all()


def test_age_lifetime_ratio_nan_for_zero_lifetime():
    df = pd.DataFrame({"launch_date": ["2015-01-01"], "expected_lifetime_yrs": [0]})
    result = add_temporal_features(df)
    assert pd.isna(result["age_lifetime_ratio"].iloc[0])
