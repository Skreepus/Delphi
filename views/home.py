import streamlit as st
import streamlit.components.v1 as components
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
        labeled = pd.read_csv(labeled_path, low_memory=False)

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

    # ── Video Background ──
    if video_src:
        st.markdown(f"""<div style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;overflow:hidden;pointer-events:none;">
<video autoplay muted loop playsinline style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);min-width:100%;min-height:100%;width:auto;height:auto;object-fit:cover;opacity:0.35;">
<source src="{video_src}" type="video/mp4">
</video>
</div>""", unsafe_allow_html=True)

    # ── All Scrollytelling Sections ──
    st.markdown(f"""
<div style="position:relative;z-index:2;">

<!-- ── Section 1: Opening ── -->
<div style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:4rem 2rem;">
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.4rem;letter-spacing:0.2em;color:#6b6560;margin-bottom:2rem;">right now, above us</p>
<p style="font-family:'Lora',serif;font-weight:500;font-size:11.2rem;color:#e8e2d9;line-height:1;margin-bottom:1rem;">{active}</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.68rem;color:#c9a96e;letter-spacing:0.15em;">satellites are orbiting Earth</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:0.98rem;color:#2a2a2a;letter-spacing:0.15em;margin-top:4rem;">scroll down. this isn't the full picture.</p>
</div>

<!-- ── Section 2: The Dead ── -->
<div style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:4rem 2rem;">
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.54rem;color:#6b6560;line-height:1.8;max-width:800px;margin-bottom:3rem;">but not all of them are alive.<br>A lot of them are just drifting.</p>
<p style="font-family:'Lora',serif;font-weight:500;font-size:9.8rem;color:#c94a4a;line-height:1;margin-bottom:1rem;">{dead}</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.54rem;color:#c94a4a;letter-spacing:0.1em;opacity:0.8;">are dead, still orbiting with no purpose.</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.54rem;color:#c94a4a;letter-spacing:0.1em;opacity:0.8;">space junk that circles our planet.</p>
</div>

<!-- ── Section 3: The Counter ── -->
<div style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:4rem 2rem;">
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.4rem;color:#6b6560;line-height:1.8;max-width:750px;margin-bottom:2.5rem;">Every 90 minutes, they circle the planet. Uncontrolled. Untracked.</p>
<div style="display:flex;flex-direction:column;align-items:center;gap:0.5rem;">
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.26rem;color:#6b6560;letter-spacing:0.1em;margin-bottom:2rem;">since you opened this page</p>
<p id="elapsed-time" style="font-family:'DM Mono',monospace;font-weight:400;font-size:5.6rem;color:#e8e2d9;letter-spacing:0.05em;">00:00:00</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.26rem;color:#6b6560;letter-spacing:0.1em;margin-bottom:2rem;">dead satellites have completed</p>
<p id="orbit-count" style="font-family:'DM Mono',monospace;font-weight:400;font-size:4.9rem;color:#c9a96e;">0</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.26rem;color:#6b6560;max-width:600px;line-height:1.8;margin-top:0.5rem;">uncontrolled orbits around Earth</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.54rem;color:#c94a4a;letter-spacing:0.1em;opacity:0.8;">a collision is bound to happen.</p>

</div>
</div>

<!-- ── Section 4: What We Built ── -->
<div style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:4rem 2rem;">
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.26rem;letter-spacing:0.2em;text-transform:uppercase;color:#c9a96e;margin-bottom:1.5rem;">introducing</p>
<p style="font-family:'Lora',serif;font-weight:500;font-size:4.9rem;color:#e8e2d9;margin-bottom:1.5rem;line-height:1.2;">The <em style="font-style:italic;color:#c9a96e;">Delphi</em><br>Project</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.4rem;color:#6b6560;line-height:1.8;max-width:800px;margin-bottom:3rem;">An orbital intelligence platform that tracks every satellite, scores every operator, and predicts failures before they happen.</p>
<div style="display:flex;gap:4rem;justify-content:center;flex-wrap:wrap;">
<div style="text-align:center;">
<p style="font-family:'DM Mono',monospace;font-weight:400;font-size:2.45rem;color:#e8e2d9;">{active}</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:0.98rem;color:#4a4540;letter-spacing:0.08em;margin-top:0.3rem;">active satellites</p>
</div>
<div style="text-align:center;">
<p style="font-family:'DM Mono',monospace;font-weight:400;font-size:2.45rem;color:#e8e2d9;">{dead}</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:0.98rem;color:#4a4540;letter-spacing:0.08em;margin-top:0.3rem;">dead in orbit</p>
</div>
<div style="text-align:center;">
<p style="font-family:'DM Mono',monospace;font-weight:400;font-size:2.45rem;color:#e8e2d9;">{operators}</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:0.98rem;color:#4a4540;letter-spacing:0.08em;margin-top:0.3rem;">operators tracked</p>
</div>
<div style="text-align:center;">
<p style="font-family:'DM Mono',monospace;font-weight:400;font-size:2.45rem;color:#c9a96e;">{high_risk}</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:0.98rem;color:#4a4540;letter-spacing:0.08em;margin-top:0.3rem;">high-risk operators</p>
</div>
</div>
</div>

<!-- ── Section 5: Product Preview Header ── -->
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:4rem 2rem 2rem 2rem;">
<p style="font-family:'Lora',serif;font-weight:500;font-size:3.4rem;color:#e8e2d9;margin-bottom:1rem;line-height:1.2;">Product Preview</p>
<p style="font-family:'Merriweather',serif;font-weight:300;font-size:1.1rem;color:#6b6560;line-height:1.8;max-width:600px;margin-bottom:2rem;">Watch how Delphi tracks, scores, and predicts satellite failures in real time.</p>
</div>

</div>
""", unsafe_allow_html=True)

    # ── YouTube Video (Streamlit native – avoids iframe nesting issue) ──
    col_left, col_video, col_right = st.columns([2, 2, 2])
    with col_video:
        st.video("https://www.youtube.com/watch?v=Ij42ss911BQ")

    st.markdown("<div style='height:6rem;position:relative;z-index:2;'></div>", unsafe_allow_html=True)

    # ── Live Counter JavaScript (uses components.html so JS actually runs) ──
    components.html(f"""
    <script>
    (function() {{
        const deadSats = {dead_count};
        const orbitPeriod = 5400;
        const startTime = Date.now();

        function update() {{
            const elapsed = (Date.now() - startTime) / 1000;

            // Timer ticks every second
            const hrs = Math.floor(elapsed / 3600);
            const mins = Math.floor((elapsed % 3600) / 60);
            const secs = Math.floor(elapsed % 60);
            const timeStr = String(hrs).padStart(2,'0') + ':' +
                           String(mins).padStart(2,'0') + ':' +
                           String(secs).padStart(2,'0');

            // Orbits increase by 1 every 4 seconds
            const totalOrbits = Math.floor(elapsed / 4);

            const parent = window.parent.document;
            const timeEl = parent.getElementById('elapsed-time');
            const orbitEl = parent.getElementById('orbit-count');

            if (timeEl) timeEl.textContent = timeStr;
            if (orbitEl) orbitEl.textContent = totalOrbits.toFixed(0);
        }}

        setInterval(update, 1000);
        update();
    }})();
    </script>
    """, height=0)

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