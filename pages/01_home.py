"""
Home page — top-level KPIs and risk overview.
"""
import streamlit as st
import pandas as pd
from components.charts import risk_distribution_chart, dead_satellites_on_orbit_chart
from utils.caching import load_master_data, load_operator_scores

st.set_page_config(page_title="Home | Orbital Credit", layout="wide")
st.title("🛰️ Orbital Credit — Overview")

df = load_master_data()
operators = load_operator_scores()

if df is None:
    st.warning("No data loaded yet. Run the data pipeline first.")
    st.stop()

# ── KPI Row ────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Satellites", f"{len(df):,}")
col2.metric("Active Satellites", f"{df[df['status'] == 'active'].shape[0]:,}")  # TODO: confirm status values
col3.metric("High-Risk Satellites", f"{(df.get('risk_tier') == 'HIGH').sum():,}")
col4.metric("Operators Tracked", f"{df['operator'].nunique():,}")

st.divider()

# ── Charts ─────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(risk_distribution_chart(df), use_container_width=True)
with c2:
    st.plotly_chart(dead_satellites_on_orbit_chart(df), use_container_width=True)
