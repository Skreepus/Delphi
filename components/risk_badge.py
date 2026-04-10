"""
Streamlit risk badge component.
Usage: from components.risk_badge import risk_badge; risk_badge("HIGH")
"""
import streamlit as st

BADGE_STYLES = {
    "HIGH":   ("🔴", "#FF4444", "HIGH RISK"),
    "MEDIUM": ("🟡", "#FFA500", "MEDIUM RISK"),
    "LOW":    ("🟢", "#22C55E", "LOW RISK"),
    "UNKNOWN": ("⚪", "#888888", "UNKNOWN"),
}

def risk_badge(tier: str) -> None:
    """Render a coloured risk badge inline."""
    icon, color, label = BADGE_STYLES.get(str(tier).upper(), BADGE_STYLES["UNKNOWN"])
    st.markdown(
        f'<span style="background:{color}20; color:{color}; border:1px solid {color}; '
        f'border-radius:4px; padding:2px 8px; font-weight:600; font-size:0.85em;">'
        f'{icon} {label}</span>',
        unsafe_allow_html=True,
    )
