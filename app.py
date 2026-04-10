"""
Orbital Credit — Main Streamlit entry point.
Run with: streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="Orbital Credit",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🛰️ Orbital Credit")
st.subheader("Predictive Compliance & Disposal-Risk Platform for Sustainable Satellite Operations")

st.markdown("""
Navigate using the sidebar to explore:
- **Home** — Summary metrics and risk overview
- **Operator Rankings** — Reliability scores by operator
- **Satellite Rankings** — High-risk active satellites
- **Operator Profile** — Drill down into a specific operator
- **Satellite Profile** — Drill down into a specific satellite
""")

# TODO: Add top-level KPI cards once data pipeline is wired up
