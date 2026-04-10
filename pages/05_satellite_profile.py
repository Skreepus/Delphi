"""
Individual satellite drill-down page.
"""
import streamlit as st
from utils.caching import load_master_data
from components.risk_badge import risk_badge

st.set_page_config(page_title="Satellite Profile | Orbital Credit", layout="wide")
st.title("🛰️ Satellite Profile")

df = load_master_data()

if df is None:
    st.warning("Data not available.")
    st.stop()

sat_name = st.selectbox("Select a satellite", df["satellite_name"].dropna().sort_values().tolist())
sat = df[df["satellite_name"] == sat_name].iloc[0]

# ── Key facts ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**Operator:** {sat.get('operator', 'N/A')}")
    st.markdown(f"**Country:** {sat.get('country', 'N/A')}")
    st.markdown(f"**Orbit Class:** {sat.get('orbit_class', 'N/A')}")
    st.markdown(f"**Launch Year:** {sat.get('launch_year', 'N/A')}")
with col2:
    st.markdown(f"**Age (yrs):** {sat.get('satellite_age_yrs', 'N/A')}")
    st.markdown(f"**Expected Lifetime:** {sat.get('expected_lifetime_yrs', 'N/A')} yrs")
    st.markdown(f"**Risk Score:** {sat.get('risk_score', 'N/A')}")
    if "risk_tier" in sat:
        risk_badge(sat["risk_tier"])

st.divider()

# ── Scoring explanation ────────────────────────────────────────────────────
st.subheader("Why this score?")
st.info("TODO: Wire up SHAP feature contributions or heuristic factor breakdown.")
