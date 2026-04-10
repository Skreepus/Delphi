"""
Operator reliability rankings page.
"""
import streamlit as st
import pandas as pd
from components.charts import top_risky_operators_chart
from components.risk_badge import risk_badge
from utils.caching import load_operator_scores

st.set_page_config(page_title="Operator Rankings | Orbital Credit", layout="wide")
st.title("📊 Operator Reliability Rankings")

operators = load_operator_scores()

if operators is None:
    st.warning("No operator scores available.")
    st.stop()

# ── Filter controls ────────────────────────────────────────────────────────
tier_filter = st.multiselect("Filter by tier", ["HIGH", "MEDIUM", "LOW"], default=["HIGH", "MEDIUM", "LOW"])
filtered = operators[operators["reliability_tier"].str.upper().isin(tier_filter)]

# ── Chart ─────────────────────────────────────────────────────────────────
st.plotly_chart(top_risky_operators_chart(filtered), use_container_width=True)

# ── Table ─────────────────────────────────────────────────────────────────
st.subheader("Full Rankings")
st.dataframe(
    filtered[["operator", "reliability_score", "reliability_tier", "total", "inactive_on_orbit"]],
    use_container_width=True,
    hide_index=True,
)
