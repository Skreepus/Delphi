"""
Score card component — shows operator or satellite score with context.
"""
import streamlit as st


def score_card(label: str, score: float, tier: str, delta: str | None = None) -> None:
    """
    Render a metric card with score and risk tier.

    Args:
        label: Card title (e.g., "Reliability Score").
        score: Numeric score to display.
        tier: Risk tier string for colour coding.
        delta: Optional delta string (e.g., "+2.3 vs last quarter").
    """
    color_map = {"HIGH": "#FF4444", "MEDIUM": "#FFA500", "LOW": "#22C55E"}
    color = color_map.get(str(tier).upper(), "#888888")

    st.markdown(
        f"""
        <div style="border:1px solid {color}; border-radius:8px; padding:16px; text-align:center;">
            <p style="margin:0; font-size:0.85em; color:#888;">{label}</p>
            <p style="margin:4px 0; font-size:2em; font-weight:700; color:{color};">{score:.1f}</p>
            {'<p style="margin:0; font-size:0.75em; color:#888;">' + delta + '</p>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
