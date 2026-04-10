"""
Display formatting helpers for the dashboard.
"""
import pandas as pd


def format_score(score: float, decimals: int = 1) -> str:
    """Format a 0–100 score for display."""
    return f"{score:.{decimals}f}"


def format_risk_score(score: float) -> str:
    """Format a 0–1 risk probability for display."""
    return f"{score * 100:.1f}%"


def clean_display_df(df: pd.DataFrame) -> pd.DataFrame:
    """General cleanup for DataFrames shown in the UI."""
    str_cols = df.select_dtypes("object").columns
    df[str_cols] = df[str_cols].fillna("—").apply(lambda col: col.str.title())
    num_cols = df.select_dtypes("number").columns
    df[num_cols] = df[num_cols].fillna(0)
    return df
