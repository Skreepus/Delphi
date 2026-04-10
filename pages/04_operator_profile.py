"""
Operator profile drill-down page.
"""
import streamlit as st
from utils.caching import load_master_data, load_operator_scores
from components.score_card import score_card
from components.risk_badge import risk_badge

st.set_page_config(page_title="Operator Profile | Orbital Credit", layout="wide")
st.title("🏢 Operator Profile")

df = load_master_data()
operators = load_operator_scores()

if df is None or operators is None:
    st.warning("Data not available.")
    st.stop()

operator_name = st.selectbox("Select an operator", operators["operator"].tolist())
op_data = operators[operators["operator"] == operator_name].iloc[0]
op_sats = df[df["operator"] == operator_name]

# ── Score summary ──────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    score_card("Reliability Score", op_data["reliability_score"], op_data["reliability_tier"])
with c2:
    st.metric("Total Satellites", int(op_data["total"]))
with c3:
    st.metric("Inactive On Orbit", int(op_data["inactive_on_orbit"]))

st.divider()

# ── Satellite table ────────────────────────────────────────────────────────
st.subheader(f"Satellites operated by {operator_name}")
st.dataframe(op_sats, use_container_width=True, hide_index=True)
