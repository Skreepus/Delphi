"""
Streamlit-cached data loaders.
All heavy I/O should go through these functions to avoid reloads.
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from config import DATA_PROCESSED


@st.cache_data(ttl=3600)
def load_master_data() -> pd.DataFrame | None:
    """Load the scored master satellite table."""
    path = DATA_PROCESSED / "master_scored.parquet"
    if not path.exists():
        # Fallback to backup CSV
        csv = DATA_PROCESSED / "master_scored.csv"
        if csv.exists():
            return pd.read_csv(csv)
        return None
    return pd.read_parquet(path)


@st.cache_data(ttl=3600)
def load_operator_scores() -> pd.DataFrame | None:
    """Load the operator reliability score table."""
    path = DATA_PROCESSED / "operator_scores.parquet"
    if not path.exists():
        csv = DATA_PROCESSED / "operator_scores.csv"
        if csv.exists():
            return pd.read_csv(csv)
        return None
    return pd.read_parquet(path)
