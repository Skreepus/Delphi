import streamlit as st
import pandas as pd
from pathlib import Path


def load_data():
    """Load the CSV files and return counts."""
    data_dir = Path("data/processed")

    stats = {
        "active_satellites": 0,
        "dead_in_orbit": 0,
        "operators_tracked": 0,
        "high_risk_operators": 0,
    }

    # ── Active satellites ──
    active_path = data_dir / "active_satellites.csv"
    if active_path.exists():
        active = pd.read_csv(active_path)
        stats["active_satellites"] = len(active)

    # ── Dead in orbit ──
    dead_path = data_dir / "dead_in_orbit.csv"
    if dead_path.exists():
        dead = pd.read_csv(dead_path)
        stats["dead_in_orbit"] = len(dead)

    # ── Labeled satellites (for operators + risk) ──
    labeled_path = data_dir / "labeled_satellites.csv"
    if labeled_path.exists():
        labeled = pd.read_csv(labeled_path)

        # Find the operator column (different datasets name it differently)
        op_col = None
        for col in ["operator", "owner", "country_operator", "operator_owner"]:
            if col in labeled.columns:
                op_col = col
                break

        if op_col:
            stats["operators_tracked"] = labeled[op_col].nunique()

            # High-risk = operators that have non_compliant satellites
            if "compliance_label" in labeled.columns:
                non_compliant = labeled[labeled["compliance_label"] == "non_compliant"]
                stats["high_risk_operators"] = non_compliant[op_col].nunique()

    return stats


def render():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600&family=Merriweather:wght@300;400;700&display=swap');

    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes countUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ── Home Page ── */
    .home-page {
        max-width: 900px;
        margin: 0 auto;
        padding: 4rem 2rem;
    }

    /* ── Hero Section ── */
    .home-hero {
        text-align: center;
        margin-bottom: 5rem;
        animation: fadeSlideUp 0.8s ease-out;
    }
    .home-eyebrow {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #c9a96e;
        margin-bottom: 1.2rem;
    }
    .home-hero h1 {
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 3.5rem;
        line-height: 1.15;
        color: #e8e2d9;
        margin-bottom: 1.5rem;
    }
    .home-hero h1 em {
        font-style: italic;
        color: #c9a96e;
    }
    .home-subtitle {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1rem;
        color: #6b6560;
        line-height: 1.9;
        max-width: 500px;
        margin: 0 auto;
    }

    /* ── Stats Grid ── */
    .stats-label {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #c9a96e;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 3rem;
    }
    .stat-card {
        background: rgba(22, 22, 22, 0.85);
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 2.2rem 2rem;
        text-align: center;
        transition: border-color 0.3s, transform 0.3s;
        animation: countUp 0.6s ease-out both;
        position: relative;
        overflow: hidden;
    }
    .stat-card:nth-child(1) { animation-delay: 0.1s; }
    .stat-card:nth-child(2) { animation-delay: 0.2s; }
    .stat-card:nth-child(3) { animation-delay: 0.3s; }
    .stat-card:nth-child(4) { animation-delay: 0.4s; }

    .stat-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #c9a96e, transparent);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .stat-card:hover {
        border-color: #c9a96e;
        transform: translateY(-3px);
    }
    .stat-card:hover::before {
        opacity: 1;
    }
    .stat-number {
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 2.8rem;
        color: #e8e2d9;
        margin-bottom: 0.5rem;
    }
    .stat-desc {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.82rem;
        color: #6b6560;
        letter-spacing: 0.05em;
        line-height: 1.5;
    }

    /* ── Warning card for high-risk ── */
    .stat-card.warning .stat-number {
        color: #c9a96e;
    }
    </style>""", unsafe_allow_html=True)

    # Load data
    stats = load_data()

    # Format numbers with commas
    active = f"{stats['active_satellites']:,}"
    dead = f"{stats['dead_in_orbit']:,}"
    operators = f"{stats['operators_tracked']:,}"
    high_risk = f"{stats['high_risk_operators']:,}"

    st.markdown(f"""<div class="home-page">

<div class="home-hero">
<p class="home-eyebrow">Overview</p>
<h1>The <em>Delphi</em><br>Project</h1>
<p class="home-subtitle">Monitoring orbital risk and satellite compliance across the global space industry.</p>
</div>

<p class="stats-label">Live Statistics</p>

<div class="stats-grid">
<div class="stat-card">
<p class="stat-number">{active}</p>
<p class="stat-desc">Active Satellites</p>
</div>
<div class="stat-card">
<p class="stat-number">{dead}</p>
<p class="stat-desc">Dead Satellites in Orbit</p>
</div>
<div class="stat-card">
<p class="stat-number">{operators}</p>
<p class="stat-desc">Operators Tracked</p>
</div>
<div class="stat-card warning">
<p class="stat-number">{high_risk}</p>
<p class="stat-desc">High-Risk Operators</p>
</div>
</div>

</div>""", unsafe_allow_html=True)