"""
Streamlit-cached data loaders.
All heavy I/O should go through these functions to avoid reloads.
"""
import streamlit as st
import pandas as pd
from pathlib import Path

from config import DATA_PROCESSED
from utils.satellite_risk_merge import load_enriched_satellite_risk_from_disk


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


@st.cache_data(ttl=3600)
def load_satellite_risk_merged() -> pd.DataFrame | None:
    """
    ML / scored rows inner-joined to master_satellites (UCS catalogue), deduplicated
    per norad_id to the best-quality row.

    Adds:
        organisation — operator name with master catalogue preferred
        data_quality_score — how complete key catalogue fields are (0–1)
        in_ucs_catalog — True for all rows when master file is present
    """
    return load_enriched_satellite_risk_from_disk()
