"""
Feature Engineering (Simplified)

Builds a flat feature table using plain pandas.
No sklearn pipelines. No black-box preprocessing.

Normalisation: z-score → (x - mean) / std
Missing values: fill with median
One-hot encoding: manual pd.get_dummies

Math required: mean, standard deviation, median (intro stats level)
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

from config import (
    LABELED_CSV,
    OPERATOR_SCORES_CSV,
    FEATURE_TABLE_CSV,
)


# ── Features the model will use ─────────────────────────────────
NUMERIC_FEATURES = [
    "age_years",
    "apogee_km",
    "perigee_km",
    "inclination_deg",
    "period_min",
    "operator_reliability_score",
    "has_lifetime_data",
]

CATEGORICAL_FEATURES = []

METADATA_COLUMNS = [
    "norad_id",
    "satellite_name",
    "operator_final",
    "compliance_label",
    "is_compliant",
]


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive satellite_age_yrs from launch_date and age_lifetime_ratio vs expected lifetime.

    age_lifetime_ratio is NaN when expected_lifetime_yrs is missing or <= 0.
    """
    df = df.copy()
    df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce")
    now = pd.Timestamp.now()
    df["satellite_age_yrs"] = (now - df["launch_date"]).dt.days / 365.25
    df["satellite_age_yrs"] = df["satellite_age_yrs"].clip(lower=0)
    if "expected_lifetime_yrs" in df.columns:
        el = pd.to_numeric(df["expected_lifetime_yrs"], errors="coerce")
        ratio = df["satellite_age_yrs"] / el
        df["age_lifetime_ratio"] = ratio.where(el > 0, np.nan)
    else:
        df["age_lifetime_ratio"] = np.nan
    return df


def add_age_feature(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate satellite age in years.

    age_years = (today - launch_date) in days / 365.25
    """
    df = add_temporal_features(df)
    df["age_years"] = df["satellite_age_yrs"]
    return df


def add_orbital_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure orbital columns are numeric.
    """
    for col in ("apogee_km", "perigee_km", "inclination_deg", "period_min"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def add_lifetime_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Binary flag: did we know this satellite's expected lifetime?

    has_lifetime_data = 1 if expected_lifetime_yrs is not NaN, else 0

    This lets the model learn that 'missing data' is itself a signal.
    """
    if "expected_lifetime_yrs" in df.columns:
        df["expected_lifetime_yrs"] = pd.to_numeric(
            df["expected_lifetime_yrs"], errors="coerce"
        )
        df["has_lifetime_data"] = df["expected_lifetime_yrs"].notna().astype(int)
    else:
        df["has_lifetime_data"] = 0
    return df


def add_operator_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Join operator reliability metrics onto each satellite.

    Uses operator_final column to match.
    """
    ops = pd.read_csv(OPERATOR_SCORES_CSV)
    print(f"  Loaded {len(ops)} operator scores")

    # Build operator_final if it doesn't exist
    if "operator_final" not in df.columns:
        df["operator_final"] = pd.array([pd.NA] * len(df), dtype="object")
        for col in ("operator_resolved", "operator_clean", "operator", "owner_code"):
            if col in df.columns:
                mask = df["operator_final"].isna() & df[col].notna()
                df.loc[mask, "operator_final"] = df.loc[mask, col].astype(str)
        df["operator_final"] = (
            df["operator_final"]
            .astype(str)
            .str.strip()
            .str.lower()
            .replace({"nan": np.nan, "": np.nan})
        )

    # Select columns from operator scores
    op_lookup = ops.rename(columns={
        "operator": "operator_final",
        "reliability_score": "operator_reliability_score",
        "raw_compliance_rate": "operator_compliance_rate",
        "inactive_ratio": "operator_inactive_ratio",
    })

    keep_cols = ["operator_final"]
    for col in ("operator_reliability_score", "operator_compliance_rate", "operator_inactive_ratio"):
        if col in op_lookup.columns:
            keep_cols.append(col)

    op_lookup = op_lookup[keep_cols].drop_duplicates(subset="operator_final")

    # Drop existing columns to avoid _x/_y conflicts
    for col in keep_cols:
        if col in df.columns and col != "operator_final":
            df = df.drop(columns=[col])

    df = df.merge(op_lookup, on="operator_final", how="left")

    # Fill missing with global averages
    if "operator_reliability_score" in df.columns:
        df["operator_reliability_score"] = df["operator_reliability_score"].fillna(
            ops["reliability_score"].mean() if "reliability_score" in ops.columns else 50.0
        )
    if "operator_compliance_rate" in df.columns:
        df["operator_compliance_rate"] = df["operator_compliance_rate"].fillna(
            ops["raw_compliance_rate"].mean() if "raw_compliance_rate" in ops.columns else 0.5
        )
    if "operator_inactive_ratio" in df.columns:
        df["operator_inactive_ratio"] = df["operator_inactive_ratio"].fillna(0.5)

    matched = df["operator_reliability_score"].notna().sum()
    print(f"  Operator features joined: {matched:,} / {len(df):,}")

    return df


def fill_missing_with_median(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Fill NaN values with the column median.

    This is the simplest reasonable imputation strategy:
    'if we don't know the value, guess the middle.'
    """
    for col in columns:
        if col in df.columns:
            median_val = df[col].median()
            missing = df[col].isna().sum()
            if missing > 0:
                df[col] = df[col].fillna(median_val)
                print(f"  {col}: filled {missing:,} missing with median {median_val:.2f}")
    return df


def one_hot_encode(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Convert a categorical column to binary columns.

    orbit_class = "LEO"  →  orbit_class_LEO=1, orbit_class_GEO=0, ...

    This is just creating separate yes/no columns for each category.
    """
    if column not in df.columns:
        return df

    dummies = pd.get_dummies(df[column], prefix=column, dtype=int)
    df = pd.concat([df, dummies], axis=1)
    return df


def build_feature_table(
    labeled_path=LABELED_CSV,
    output_path=FEATURE_TABLE_CSV,
) -> pd.DataFrame:
    """
    Build the complete feature table.

    Steps:
        1. Load labeled satellites
        2. Calculate satellite age
        3. Ensure orbital features are numeric
        4. Add lifetime flag
        5. Join operator scores
        6. Fill missing values with median
        7. One-hot encode orbit_class
        8. Save
    """
    print("=" * 60)
    print("BUILDING FEATURE TABLE")
    print("=" * 60)

    # ── Load ────────────────────────────────────────────────────
    print(f"\nLoading: {labeled_path}")
    df = pd.read_csv(labeled_path, low_memory=False)
    print(f"  Rows: {len(df):,}")

    # ── Add features ────────────────────────────────────────────
    print("\n── Step 1: Satellite age ──")
    df = add_age_feature(df)

    print("\n── Step 2: Orbital features ──")
    df = add_orbital_features(df)

    print("\n── Step 3: Lifetime flag ──")
    df = add_lifetime_flag(df)

    print("\n── Step 4: Operator features ──")
    df = add_operator_features(df)

    print("\n── Step 5: Fill missing values ──")
    df = fill_missing_with_median(df, NUMERIC_FEATURES)

    print("\n── Step 6: One-hot encode categoricals ──")
    for cat_col in CATEGORICAL_FEATURES:
        df = one_hot_encode(df, cat_col)
    if not CATEGORICAL_FEATURES:
        print("  No categorical features to encode")
    # ── Report ──────────────────────────────────────────────────
    # Find all orbit_class_ columns created by one-hot encoding
    orbit_dummies = [c for c in df.columns if c.startswith("orbit_class_")]

    all_model_features = NUMERIC_FEATURES + orbit_dummies
    print(f"\n── Feature Summary ──")
    print(f"  Numeric features: {len(NUMERIC_FEATURES)}")
    print(f"  Orbit class dummies: {len(orbit_dummies)} → {orbit_dummies}")
    print(f"  Total model features: {len(all_model_features)}")

    train = df[df["compliance_label"].isin(["compliant", "non_compliant"])]
    predict = df[df["compliance_label"] == "unknown"]
    print(f"\n  Training set:    {len(train):,}")
    print(f"  Prediction set:  {len(predict):,}")

    # ── Save ────────────────────────────────────────────────────
    output_dir = os.path.dirname(str(output_path))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    df.to_csv(output_path, index=False)
    print(f"\n✅ Saved to {output_path}")
    print(f"   {len(df):,} rows")

    return df


if __name__ == "__main__":
    build_feature_table()