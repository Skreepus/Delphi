import pandas as pd
import numpy as np
from datetime import datetime


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    now = datetime.now()

    df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce")
    df["launch_year"] = df["launch_date"].dt.year
    df["satellite_age_yrs"] = (now.year - df["launch_year"]).clip(lower=0)

    df["age_lifetime_ratio"] = np.where(
        df["expected_lifetime_yrs"].fillna(0) > 0,
        df["satellite_age_yrs"] / df["expected_lifetime_yrs"],
        np.nan,
    )
    return df


def add_operator_aggregate_features(df: pd.DataFrame) -> pd.DataFrame:
    agg = df.groupby("operator").agg(
        operator_total_launched=("satellite_name", "count"),
        operator_inactive_on_orbit=("is_inactive", "sum"),
        operator_compliance_rate=("is_compliant", "mean"),
    ).reset_index()

    return df.merge(agg, on="operator", how="left")


def build_feature_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches the dataset with satellite age info and operator performance statistics.
    """
    df = add_temporal_features(df)
    df = add_operator_aggregate_features(df)
    return df