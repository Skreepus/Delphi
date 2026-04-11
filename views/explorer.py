"""
Explorer — embedded Space Risk Radar (Cesium) matching Delphi Streamlit theme.

Production: set ``DELPHI_RADAR_URL`` to the deployed radar UI origin.
Development default: ``http://localhost:5173`` (Vite).
"""
from __future__ import annotations

import os

import streamlit as st

from views.delphi_theme import inject_global_layout

RADAR_URL = os.getenv("DELPHI_RADAR_URL", "http://localhost:5173")


def render() -> None:
    inject_global_layout()
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Merriweather:wght@300;400;700&display=swap');

.explorer-wrap {
    max-width: 42rem;
    margin: 0 auto;
    padding: 0.5rem 0.75rem 1rem;
    box-sizing: border-box;
}
.explorer-eyebrow {
    font-family: "Merriweather", serif;
    font-weight: 300;
    font-size: clamp(0.65rem, 2vw, 0.75rem);
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #c9a96e;
    margin-bottom: 0.75rem;
    text-align: center;
}
.explorer-title {
    font-family: "Cormorant Garamond", serif;
    font-weight: 500;
    font-size: clamp(1.85rem, 5vw, 2.75rem);
    color: #e8e2d9;
    text-align: center;
    margin: 0 0 0.5rem 0;
    line-height: 1.15;
}
.explorer-title em {
    font-style: italic;
    color: #c9a96e;
}
.explorer-sub {
    font-family: "Merriweather", serif;
    font-weight: 300;
    font-size: clamp(0.9rem, 2.2vw, 0.98rem);
    color: #6b6560;
    text-align: center;
    max-width: 36rem;
    margin: 0 auto 0.75rem;
    line-height: 1.75;
}
.explorer-hint {
    font-family: "Merriweather", serif;
    font-size: clamp(0.78rem, 2vw, 0.85rem);
    color: #4a4540;
    text-align: center;
    margin-bottom: 1rem;
    line-height: 1.6;
}
.explorer-about {
    font-family: "Merriweather", serif;
    font-weight: 300;
    font-size: 0.92rem;
    color: #8a8478;
    line-height: 1.75;
}
.explorer-about h3 {
    font-family: "Cormorant Garamond", serif;
    font-weight: 500;
    font-size: 1.05rem;
    color: #c9a96e;
    margin: 0 0 0.65rem 0;
    letter-spacing: 0.06em;
}
.explorer-about p { margin: 0 0 0.85rem 0; }
.explorer-about p:last-child { margin-bottom: 0; }
.explorer-about ul {
    margin: 0.35rem 0 0.85rem 1.1rem;
    padding: 0;
}
.explorer-about li { margin-bottom: 0.4rem; }
</style>


""",
        unsafe_allow_html=True,
    )

    with st.expander("About this explorer", expanded=False):
        st.markdown(
            f"""
<div class="explorer-about">

<h3>What you are seeing</h3>
<p>This module reads the same enriched satellite dataset as the rest of Delphi risk scores,
operator reliability, and orbit class served to the globe by the Delphi API. The view below
is the Space Risk Radar interface</p>

<h3>How to read the globe</h3>
<ul>
<li><strong style="color:#c9a96e;">Colour</strong> — disposal risk score (greener = lower, redder = higher).</li>
<li><strong style="color:#c9a96e;">Size &amp; outline</strong> — operator reliability tier (larger / stronger outline = higher reliability).</li>
</ul>

</div>
""",
            unsafe_allow_html=True,
        )

    try:
        with st.container(border=True):
            st.iframe(
                RADAR_URL,
                width="stretch",
                height=900,
            )
    except Exception as exc:
        st.error(f"Could not embed the radar ({exc}).")
