import streamlit as st
import pandas as pd
import base64
from pathlib import Path


def get_base64_video(video_path):
    """Convert video to base64 for HTML embedding."""
    file = Path(video_path)
    if not file.exists():
        return ""
    video_bytes = file.read_bytes()
    encoded = base64.b64encode(video_bytes).decode()
    return f"data:video/mp4;base64,{encoded}"


def load_data():
    """Load the CSV files and return counts."""
    data_dir = Path("data/processed")

    stats = {
        "active_satellites": 0,
        "dead_in_orbit": 0,
        "operators_tracked": 0,
        "high_risk_operators": 0,
    }

    active_path = data_dir / "active_satellites.csv"
    if active_path.exists():
        active = pd.read_csv(active_path)
        stats["active_satellites"] = len(active)

    dead_path = data_dir / "dead_in_orbit.csv"
    if dead_path.exists():
        dead = pd.read_csv(dead_path)
        stats["dead_in_orbit"] = len(dead)

    labeled_path = data_dir / "labeled_satellites.csv"
    if labeled_path.exists():
        labeled = pd.read_csv(labeled_path)

        op_col = None
        for col in ["operator", "owner", "country_operator", "operator_owner"]:
            if col in labeled.columns:
                op_col = col
                break

        if op_col:
            stats["operators_tracked"] = labeled[op_col].nunique()

            if "compliance_label" in labeled.columns:
                non_compliant = labeled[labeled["compliance_label"] == "non_compliant"]
                stats["high_risk_operators"] = non_compliant[op_col].nunique()

    return stats


def render():
    video_src = get_base64_video("assets/stars.mp4")
    stats = load_data()

    active = f"{stats['active_satellites']:,}"
    dead = f"{stats['dead_in_orbit']:,}"
    operators = f"{stats['operators_tracked']:,}"
    high_risk = f"{stats['high_risk_operators']:,}"

    dead_count = stats['dead_in_orbit'] if stats['dead_in_orbit'] > 0 else 3200

    st.markdown(f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600&family=Merriweather:wght@300;400;700&family=DM+Mono:wght@300;400&display=swap');

    /* ── Video Background ── */
    .video-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 0;
        overflow: hidden;
        pointer-events: none;
    }}
    .video-bg video {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        min-width: 100%;
        min-height: 100%;
        width: auto;
        height: auto;
        object-fit: cover;
        opacity: 0.35;
    }}
    .video-bg::after {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            180deg,
            rgba(13,13,13,0.3) 0%,
            rgba(13,13,13,0.1) 30%,
            rgba(13,13,13,0.1) 70%,
            rgba(13,13,13,0.6) 100%
        );
    }}

    /* ── Scroll Container ── */
    .scroll-home {{
        position: relative;
        z-index: 2;
    }}

    /* ── Each Section = Full Viewport ── */
    .scroll-section {{
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 4rem 2rem;
    }}

    /* ── Animations ── */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(40px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes pulseGlow {{
        0%, 100% {{ opacity: 0.6; }}
        50% {{ opacity: 1; }}
    }}

    /* ── Section 1: Opening ── */
    .opening-label {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.85rem;
        letter-spacing: 0.2em;
        color: #6b6560;
        margin-bottom: 2rem;
        animation: fadeIn 1s ease-out;
    }}
    .opening-number {{
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 8rem;
        color: #e8e2d9;
        line-height: 1;
        margin-bottom: 1rem;
        animation: fadeIn 1s ease-out 0.3s both;
    }}
    .opening-unit {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1.1rem;
        color: #c9a96e;
        letter-spacing: 0.15em;
        animation: fadeIn 1s ease-out 0.6s both;
    }}
    .scroll-hint {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.7rem;
        color: #2a2a2a;
        letter-spacing: 0.15em;
        margin-top: 4rem;
        animation: pulseGlow 3s ease-in-out infinite;
    }}

    /* ── Section 2: The Dead ── */
    .dead-intro {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1rem;
        color: #6b6560;
        line-height: 2;
        max-width: 500px;
        margin-bottom: 3rem;
    }}
    .dead-number {{
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 6rem;
        color: #c94a4a;
        line-height: 1;
        margin-bottom: 1rem;
    }}
    .dead-label {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1rem;
        color: #c94a4a;
        letter-spacing: 0.1em;
        opacity: 0.8;
    }}

    /* ── Section 3: The Counter ── */
    .counter-intro {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.9rem;
        color: #6b6560;
        line-height: 2;
        max-width: 450px;
        margin-bottom: 2.5rem;
    }}
    .counter-wrap {{
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }}
    .counter-time {{
        font-family: "DM Mono", monospace;
        font-weight: 400;
        font-size: 3.5rem;
        color: #e8e2d9;
        letter-spacing: 0.05em;
    }}
    .counter-label {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.8rem;
        color: #6b6560;
        letter-spacing: 0.1em;
        margin-bottom: 2rem;
    }}
    .orbit-count {{
        font-family: "DM Mono", monospace;
        font-weight: 400;
        font-size: 2.5rem;
        color: #c9a96e;
    }}
    .orbit-label {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.85rem;
        color: #6b6560;
        max-width: 400px;
        line-height: 1.8;
        margin-top: 0.5rem;
    }}
    .orbit-sub {{
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.75rem;
        color: #4a4540;
        margin-top: 2rem;
    }}

    /* ── Section 4: What We Built ── */
    .built-eyebrow {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #c9a96e;
        margin-bottom: 1.5rem;
    }}
    .built-title {{
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 3rem;
        color: #e8e2d9;
        margin-bottom: 1.5rem;
        line-height: 1.2;
    }}
    .built-title em {{
        font-style: italic;
        color: #c9a96e;
    }}
    .built-desc {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.95rem;
        color: #6b6560;
        line-height: 2;
        max-width: 520px;
        margin-bottom: 3rem;
    }}

    /* ── Stats Bar ── */
    .stats-bar {{
        display: flex;
        gap: 3rem;
        justify-content: center;
        flex-wrap: wrap;
    }}
    .stats-bar-item {{
        text-align: center;
    }}
    .stats-bar-num {{
        font-family: "DM Mono", monospace;
        font-weight: 400;
        font-size: 1.4rem;
        color: #e8e2d9;
    }}
    .stats-bar-num.warning {{
        color: #c9a96e;
    }}
    .stats-bar-label {{
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.7rem;
        color: #4a4540;
        letter-spacing: 0.08em;
        margin-top: 0.3rem;
    }}
    </style>""", unsafe_allow_html=True)

    # ── Video Background ──
    if video_src:
        st.markdown(f"""<div class="video-bg">
<video autoplay muted loop playsinline>
<source src="{video_src}" type="video/mp4">
</video>
</div>""", unsafe_allow_html=True)

    # ── Scrollytelling Sections ──
    st.markdown(f"""<div class="scroll-home">

<div class="scroll-section">
<p class="opening-label">right now, above us</p>
<p class="opening-number">{active}</p>
<p class="opening-unit">satellites are orbiting Earth</p>
<p class="scroll-hint">scroll</p>
</div>

<div class="scroll-section">
<p class="dead-intro">But not all of them are alive.<br>Not all of them are under control.</p>
<p class="dead-number">{dead}</p>
<p class="dead-label">are dead — still orbiting, still a collision risk</p>
</div>

<div class="scroll-section">
<p class="counter-intro">Every 90 minutes, each dead satellite completes a full orbit at 28,000 km/h. Uncontrolled. Untracked. A collision waiting to happen.</p>
<div class="counter-wrap">
<p class="counter-label">since you opened this page</p>
<p class="counter-time" id="elapsed-time">00:00:00</p>
<p class="counter-label">dead satellites have completed</p>
<p class="orbit-count" id="orbit-count">0.0</p>
<p class="orbit-label">uncontrolled orbits around Earth</p>
<p class="orbit-sub" id="pass-count">0 potential collision passes</p>
</div>
</div>

<div class="scroll-section">
<p class="built-eyebrow">introducing</p>
<p class="built-title">The <em>Delphi</em><br>Project</p>
<p class="built-desc">We built an orbital intelligence platform that tracks every satellite, scores every operator, and predicts failures before they happen.</p>
<div class="stats-bar">
<div class="stats-bar-item">
<p class="stats-bar-num">{active}</p>
<p class="stats-bar-label">active satellites</p>
</div>
<div class="stats-bar-item">
<p class="stats-bar-num">{dead}</p>
<p class="stats-bar-label">dead in orbit</p>
</div>
<div class="stats-bar-item">
<p class="stats-bar-num">{operators}</p>
<p class="stats-bar-label">operators tracked</p>
</div>
<div class="stats-bar-item">
<p class="stats-bar-num warning">{high_risk}</p>
<p class="stats-bar-label">high-risk operators</p>
</div>
</div>
</div>

</div>""", unsafe_allow_html=True)

    # ── Live Counter JavaScript ──
    st.markdown(f"""
<script>
(function() {{
    const startTime = Date.now();
    const deadSats = {dead_count};
    const orbitPeriod = 5400;

    function update() {{
        const elapsed = (Date.now() - startTime) / 1000;
        const hrs = Math.floor(elapsed / 3600);
        const mins = Math.floor((elapsed % 3600) / 60);
        const secs = Math.floor(elapsed % 60);
        const timeStr = String(hrs).padStart(2,'0') + ':' +
                       String(mins).padStart(2,'0') + ':' +
                       String(secs).padStart(2,'0');
        const orbitsPerSat = elapsed / orbitPeriod;
        const totalOrbits = orbitsPerSat * deadSats;
        const passes = Math.floor(totalOrbits * 16);
        const timeEl = document.getElementById('elapsed-time');
        const orbitEl = document.getElementById('orbit-count');
        const passEl = document.getElementById('pass-count');
        if (timeEl) timeEl.textContent = timeStr;
        if (orbitEl) orbitEl.textContent = totalOrbits.toFixed(1);
        if (passEl) passEl.textContent = passes.toLocaleString() + ' potential collision passes';
        requestAnimationFrame(update);
    }}
    update();
}})();
</script>
""", unsafe_allow_html=True)

    # ── Navigation Buttons ──
    st.markdown("""<div style="height: 2rem; position: relative; z-index: 10;"></div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Operator Rankings", key="nav_rankings", use_container_width=True):
            st.session_state.page = "operator_rankings"
            st.rerun()

    # ── Style the navigation buttons ──
    st.markdown("""<style>
    div[data-testid="stHorizontalBlock"] {
        position: relative !important;
        z-index: 10 !important;
    }
    div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
        background: rgba(22, 22, 22, 0.85) !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 8px !important;
        padding: 2rem 2rem !important;
        font-family: "Lora", serif !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
        color: #e8e2d9 !important;
        transition: all 0.3s ease !important;
        float: none !important;
        position: relative !important;
        z-index: 10 !important;
    }
    div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
        border-color: #c9a96e !important;
        transform: translateY(-3px) !important;
        background: rgba(30, 28, 24, 0.9) !important;
        color: #c9a96e !important;
    }
    </style>""", unsafe_allow_html=True)