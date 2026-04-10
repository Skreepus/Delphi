"""
High-risk active satellite rankings page.
"""
import streamlit as st
import pandas as pd
from utils.caching import load_master_data

st.set_page_config(page_title="Satellite Rankings | Orbital Credit", layout="wide")
st.title("🛰️ High-Risk Active Satellites")

df = load_master_data()

if df is None:
    st.warning("No satellite data available.")
    st.stop()

# ── Filter controls ────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    orbit_filter = st.multiselect("Orbit class", df["orbit_class"].dropna().unique().tolist())
with col2:
    country_filter = st.multiselect("Country", df["country"].dropna().unique().tolist())

display = df.copy()
if orbit_filter:
    display = display[display["orbit_class"].isin(orbit_filter)]
if country_filter:
    display = display[display["country"].isin(country_filter)]

# Show top 100 by risk score
top = display.sort_values("risk_score", ascending=False).head(100)

COLS = ["satellite_name", "operator", "country", "orbit_class", "risk_score", "risk_tier", "satellite_age_yrs"]
available_cols = [c for c in COLS if c in top.columns]

st.dataframe(top[available_cols], use_container_width=True, hide_index=True)
