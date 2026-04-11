import streamlit as st
from views import home, about
from views.delphi_theme import inject_global_layout

st.set_page_config(page_title="Delphi Project", layout="wide")

# ── DEVELOPMENT TOGGLE ──────────────────────────────────────────────────────
SHOW_CENTER_GUIDE = False

# ── Session state for page routing ─────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Merriweather:wght@300;400;700&display=swap');

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
.block-container { padding-top: 0 !important; }

/* ── Sticky Navbar ── */
[data-testid="stMain"] > div:first-child {
    position: sticky !important;
    top: 0 !important;
    z-index: 999 !important;
    background: #0d0d0d !important;
}

/* Root variables */
:root {
    --bg: #0d0d0d;
    --surface: #161616;
    --border: #2a2a2a;
    --text: #e8e2d9;
    --muted: #6b6560;
    --accent: #c9a96e;
}

body, .stApp {
    background-color: #0d0d0d !important;
    color: #e8e2d9;
}

.bg-earth {
    visibility: hidden;
}

/* ── Hero ── */
.hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: calc(100vh - 64px);
    text-align: center;
    padding: 4rem 2rem;
}
.eyebrow {
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #c9a96e;
    margin-bottom: 1.2rem;
}
.hero h1 {
    font-family: "Cormorant Garamond", serif;
    font-optical-sizing: auto;
    font-weight: 300;
    font-size: 4.5rem;
    line-height: 1.1;
    color: #e8e2d9;
    margin-bottom: 1.5rem;
}
.hero h1 em { font-style: italic; color: #c9a96e; }
.hero p {
    font-size: 0.8rem;
    color: #6b6560;
    max-width: 380px;
    line-height: 1.9;
}

/* ── Center Guide Line ── */
.center-guide {
    position: fixed;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 1px;
    height: 100vh;
    background-color: rgba(201, 169, 110, 0.6);
    z-index: 9999;
    pointer-events: none;
}

.center-guide::before {
    content: "← CENTER →";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-90deg);
    background: rgba(201, 169, 110, 0.9);
    color: #0d0d0d;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    padding: 2px 6px;
    white-space: nowrap;
    border-radius: 4px;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

inject_global_layout()

# ── Conditionally show center guide ─────────────────────────────────────────
if SHOW_CENTER_GUIDE:
    st.markdown('<div class="center-guide"></div>', unsafe_allow_html=True)

# ── Navbar ─────────────────────────────────────────────────────────────────
col_logo, col_spacer, col_rankings, col_overview, col_explorer, col_about = st.columns(
    [1.2, 1.2, 0.72, 0.72, 0.72, 0.5]
)

with col_logo:
    if st.button("delphi-project", key="logo_btn"):
        st.session_state.page = "home"
        st.rerun()

with col_rankings:
    if st.button("rankings", key="rankings_btn"):
        st.session_state.page = "operator_rankings"
        st.rerun()

with col_overview:
    if st.button("overview", key="overview_btn"):
        st.session_state.page = "satellite_overview"
        st.rerun()

with col_explorer:
    if st.button("explorer", key="explorer_btn"):
        st.session_state.page = "satellite_explorer"
        st.rerun()

with col_about:
    if st.button("about us", key="about_btn"):
        st.session_state.page = "about"
        st.rerun()

st.markdown("<hr style='border-color:#2a2a2a; margin:0;'>", unsafe_allow_html=True)

# ── Page routing ────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    home.render()

elif st.session_state.page == "about":
    about.render()

elif st.session_state.page == "operator_rankings":
    from views import operator_rankings
    operator_rankings.render()

elif st.session_state.page == "satellite_explorer":
    from views import explorer

    explorer.render()

elif st.session_state.page == "satellite_overview":
    from views import satellite_overview_lay
    satellite_overview_lay.render()

st.markdown(
    """
<footer class="delphi-site-footer">
<p>Delphi — orbital risk insight from public catalogue data. Scores are model estimates, not official safety ratings.</p>
</footer>
<style>
.delphi-site-footer {
    margin-top: 2.5rem;
    padding: 1.5rem max(1rem, env(safe-area-inset-right)) 2rem max(1rem, env(safe-area-inset-left));
    text-align: center;
    border-top: 1px solid #2a2a2a;
    font-family: "Merriweather", Georgia, serif;
    font-size: 0.78rem;
    font-weight: 300;
    color: #4a4540;
    letter-spacing: 0.04em;
    line-height: 1.65;
    max-width: min(720px, 100%);
    margin-left: auto;
    margin-right: auto;
}
.delphi-site-footer p { margin: 0; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Navbar button styling ───────────────────────────────────────────────────
st.markdown("""
<style>
/* ============================================================
   LOGO BUTTON — "delphi-project" — Cormorant Garamond Medium 500
   ============================================================ */
[data-testid="stBaseButton-secondary"]:first-child,
[data-testid="stBaseButton-secondary"]:first-child p,
[data-testid="stBaseButton-secondary"]:first-child span {
    font-family: "Cormorant Garamond", serif !important;
    font-optical-sizing: auto !important;
    font-weight: 500 !important;
    font-style: normal !important;
    font-size: 2.0rem !important;
    color: #c9a96e !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
    letter-spacing: 0.02em;
    white-space: nowrap;
    line-height: 1.2 !important;
}
[data-testid="stBaseButton-secondary"]:first-child:hover {
    opacity: 0.7;
    color: #c9a96e !important;
}

/* ============================================================
   ALL NAV BUTTONS — shared resets
   ============================================================ */
section[data-testid="stMain"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    cursor: pointer;
}

/* ============================================================
   NAV LINK BUTTONS — rankings + explorer + about us
   ============================================================ */
button[kind="secondary"],
button[kind="secondary"] p,
button[kind="secondary"] span {
    font-family: "Cormorant Garamond", serif !important;
    font-optical-sizing: auto !important;
    font-weight: 500 !important;
    font-style: normal !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.02em !important;
    color: #6b6560 !important;
    float: none !important;
    text-align: center !important;
}
button[kind="secondary"]:hover,
button[kind="secondary"]:hover p,
button[kind="secondary"]:hover span {
    color: #c9a96e !important;
}
</style>
""", unsafe_allow_html=True)