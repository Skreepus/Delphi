import base64
import streamlit as st
import pandas as pd
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_sat_image_uri() -> str:
    """Return a data-URI for the satellite PNG, or empty string on failure."""
    img = _PROJECT_ROOT / "assets" / "sat1.jpg"
    if not img.is_file():
        return ""
    b64 = base64.b64encode(img.read_bytes()).decode()
    return f"data:image/jpeg;base64,{b64}"


def load_operator_data():
    path = Path("data/processed/operator_scores.csv")
    if not path.exists():
        return None
    return pd.read_csv(path)


def _tier_color(tier: str) -> str:
    t = tier.strip().lower()
    if t == "low":
        return "#c94a4a"
    if t == "medium":
        return "#c9a96e"
    return "#4a9c6e"


def _tier_bg(tier: str) -> str:
    t = tier.strip().lower()
    if t == "low":
        return "rgba(201,74,74,0.08)"
    if t == "medium":
        return "rgba(201,169,110,0.08)"
    return "rgba(74,156,110,0.08)"


def _tier_border(tier: str) -> str:
    t = tier.strip().lower()
    if t == "low":
        return "rgba(201,74,74,0.2)"
    if t == "medium":
        return "rgba(201,169,110,0.2)"
    return "rgba(74,156,110,0.2)"


def _lead_arrow(a_better: bool | None) -> tuple[str, str]:
    """Return (indicator_a, indicator_b) — a small triangle for the leader."""
    if a_better is None:
        return "", ""
    if a_better:
        return '<span class="cmp-lead">&#9650;</span>', ""
    return "", '<span class="cmp-lead">&#9650;</span>'


def render():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600&family=Merriweather:wght@300;400;700&family=DM+Mono:wght@300;400&display=swap');

    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(24px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Page ── */
    .cmp-page {
        max-width: 1060px;
        margin: 0 auto;
        padding: 3.5rem 2rem 4rem;
    }
    .cmp-header {
        text-align: center;
        margin-bottom: 2.5rem;
        animation: fadeSlideUp 0.7s ease-out;
    }
    .cmp-eyebrow {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: #c9a96e;
        margin-bottom: 1rem;
    }
    .cmp-title {
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 3rem;
        color: #e8e2d9;
        margin-bottom: 0.8rem;
        line-height: 1.15;
    }
    .cmp-subtitle {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1.05rem;
        color: #6b6560;
        line-height: 1.8;
        max-width: 560px;
        margin: 0 auto;
        text-align: center;
    }

    /* ── Operator profile cards at top ── */
    .cmp-profiles {
        display: grid;
        grid-template-columns: 1fr 60px 1fr;
        align-items: stretch;
        gap: 0;
        margin-bottom: 0;
        animation: fadeSlideUp 0.7s ease-out 0.08s both;
    }
    .cmp-profile {
        background: rgba(22, 22, 22, 0.65);
        border: 1px solid #2a2a2a;
        border-radius: 10px 10px 0 0;
        padding: 2rem 1.5rem 1.6rem;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.6rem;
    }
    .cmp-profile-name {
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 1.55rem;
        color: #e8e2d9;
        line-height: 1.25;
        margin: 0;
    }
    .cmp-profile-score {
        font-family: "DM Mono", monospace;
        font-weight: 400;
        font-size: 2.6rem;
        line-height: 1;
        margin: 0.3rem 0 0.15rem;
    }
    .cmp-profile-score-label {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.78rem;
        color: #4a4540;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .cmp-profile-bar {
        width: 80%;
        max-width: 180px;
        height: 4px;
        background: #1a1a1a;
        border-radius: 2px;
        overflow: hidden;
        margin-top: 0.25rem;
    }
    .cmp-profile-bar-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 0.8s ease;
    }
    .cmp-profile-tier {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.75rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 3px 14px;
        border-radius: 4px;
        display: inline-block;
        margin-top: 0.2rem;
    }
    .cmp-vs-col {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .cmp-vs-badge {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.85rem;
        color: #3a3a3a;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    /* ── Comparison table ── */
    .cmp-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        animation: fadeSlideUp 0.7s ease-out 0.16s both;
    }
    .cmp-table th {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.75rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #4a4540;
        padding: 1rem 1.2rem 0.8rem;
        border-bottom: 1px solid #2a2a2a;
    }
    .cmp-table th.metric-col { text-align: left; width: 34%; }
    .cmp-table th.val-col    { text-align: center; width: 33%; }

    .cmp-table td {
        padding: 1rem 1.2rem;
        border-bottom: 1px solid rgba(42,42,42,0.4);
        vertical-align: middle;
    }
    .cmp-table tr:last-child td {
        border-bottom: none;
    }
    .cmp-table tr {
        transition: background 0.2s ease;
    }
    .cmp-table tbody tr:hover {
        background: rgba(30, 28, 24, 0.45);
    }

    .cmp-metric {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.92rem;
        color: #8a8478;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .cmp-metric-icon {
        font-size: 0.75rem;
        opacity: 0.4;
    }

    .cmp-cell {
        text-align: center;
    }
    .cmp-val {
        font-family: "DM Mono", monospace;
        font-weight: 400;
        font-size: 1.15rem;
        color: #e8e2d9;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }
    .cmp-lead {
        font-size: 0.55rem;
        color: #4a9c6e;
        line-height: 1;
    }

    .cmp-cell-bar {
        width: 70%;
        max-width: 140px;
        height: 3px;
        background: #1a1a1a;
        border-radius: 2px;
        overflow: hidden;
        margin: 0.35rem auto 0;
    }
    .cmp-cell-bar-fill {
        height: 100%;
        border-radius: 2px;
    }

    .cmp-badge-sm {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 3px 11px;
        border-radius: 3px;
        display: inline-block;
    }

    /* ── Table wrapper ── */
    .cmp-table-wrap {
        background: rgba(22, 22, 22, 0.5);
        border: 1px solid #2a2a2a;
        border-top: none;
        border-radius: 0 0 10px 10px;
        overflow: hidden;
        margin-bottom: 2rem;
    }

    /* ── Verdict ── */
    .cmp-verdict {
        background: rgba(22, 22, 22, 0.5);
        border: 1px solid #2a2a2a;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        animation: fadeSlideUp 0.7s ease-out 0.24s both;
    }
    .cmp-verdict-label {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.8rem;
        color: #6b6560;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .cmp-verdict-name {
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 1.6rem;
        color: #4a9c6e;
        margin-bottom: 0.25rem;
    }
    .cmp-verdict-detail {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.85rem;
        color: #4a4540;
    }
    .cmp-verdict-tie {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1.1rem;
        color: #6b6560;
    }

    .cmp-empty {
        text-align: center;
        font-family: "Merriweather", serif;
        font-weight: 300;
        color: #6b6560;
        padding: 3rem 1rem;
    }

    @media (max-width: 720px) {
        .cmp-title { font-size: clamp(1.6rem, 5vw, 2.4rem) !important; }
        .cmp-profiles { grid-template-columns: 1fr 40px 1fr !important; }
        .cmp-profile { padding: 1.4rem 1rem !important; }
        .cmp-profile-name { font-size: 1.15rem !important; }
        .cmp-profile-score { font-size: 2rem !important; }
        .cmp-val { font-size: 1rem !important; }
        .cmp-metric { font-size: 0.82rem !important; }
    }
    </style>""", unsafe_allow_html=True)

    df = load_operator_data()

    if df is None or len(df) == 0:
        st.markdown("""<div class="cmp-page">
<div class="cmp-header">
<p class="cmp-title">Operator Comparison</p>
<p class="cmp-subtitle">No data available. Run the scoring pipeline first.</p>
</div></div>""", unsafe_allow_html=True)
        return

    operators = sorted(df["operator_display"].dropna().unique().tolist())

    col_a, col_b = st.columns(2)
    with col_a:
        op_a = st.selectbox("Operator A", operators, index=0, key="cmp_op_a")
    with col_b:
        default_b = min(1, len(operators) - 1)
        op_b = st.selectbox("Operator B", operators, index=default_b, key="cmp_op_b")

    if op_a == op_b:
        st.markdown('<p class="cmp-empty">Select two different operators to compare.</p>', unsafe_allow_html=True)
        return

    row_a = df[df["operator_display"] == op_a].iloc[0]
    row_b = df[df["operator_display"] == op_b].iloc[0]

    tier_a = str(row_a["reliability_tier"]).strip().lower()
    tier_b = str(row_b["reliability_tier"]).strip().lower()
    score_a = float(row_a["reliability_score"])
    score_b = float(row_b["reliability_score"])
    comp_a = float(row_a["compliance_rate_smoothed"]) * 100
    comp_b = float(row_b["compliance_rate_smoothed"]) * 100
    fleet_a = int(row_a["total_objects"])
    fleet_b = int(row_b["total_objects"])
    dead_a = int(row_a["inactive_on_orbit"])
    dead_b = int(row_b["inactive_on_orbit"])
    ratio_a = float(row_a["inactive_ratio"]) * 100
    ratio_b = float(row_b["inactive_ratio"]) * 100
    comp_comp_a = float(row_a["compliance_component"])
    comp_comp_b = float(row_b["compliance_component"])
    debris_a = float(row_a["debris_component"])
    debris_b = float(row_b["debris_component"])

    tc_a, tc_b = _tier_color(tier_a), _tier_color(tier_b)
    bg_a, bg_b = _tier_bg(tier_a), _tier_bg(tier_b)
    bd_a, bd_b = _tier_border(tier_a), _tier_border(tier_b)

    compliant_a = "Compliant" if comp_a >= 50 else "Non-compliant"
    compliant_b = "Compliant" if comp_b >= 50 else "Non-compliant"
    cc_a = "#4a9c6e" if comp_a >= 50 else "#c94a4a"
    cc_b = "#4a9c6e" if comp_b >= 50 else "#c94a4a"
    ccbg_a = "rgba(74,156,110,0.08)" if comp_a >= 50 else "rgba(201,74,74,0.08)"
    ccbg_b = "rgba(74,156,110,0.08)" if comp_b >= 50 else "rgba(201,74,74,0.08)"
    ccbd_a = "rgba(74,156,110,0.2)" if comp_a >= 50 else "rgba(201,74,74,0.2)"
    ccbd_b = "rgba(74,156,110,0.2)" if comp_b >= 50 else "rgba(201,74,74,0.2)"

    # Determine who leads each metric (higher is better for score/compliance, lower is better for dead/ratio)
    score_lead = None if score_a == score_b else (score_a > score_b)
    comp_lead = None if comp_a == comp_b else (comp_a > comp_b)
    dead_lead = None if dead_a == dead_b else (dead_a < dead_b)
    ratio_lead = None if ratio_a == ratio_b else (ratio_a < ratio_b)
    comp_comp_lead = None if comp_comp_a == comp_comp_b else (comp_comp_a > comp_comp_b)
    debris_lead = None if debris_a == debris_b else (debris_a < debris_b)

    ar_score = _lead_arrow(score_lead)
    ar_comp = _lead_arrow(comp_lead)
    ar_dead = _lead_arrow(dead_lead)
    ar_ratio = _lead_arrow(ratio_lead)
    ar_cc = _lead_arrow(comp_comp_lead)
    ar_deb = _lead_arrow(debris_lead)

    # Count wins
    metrics = [score_lead, comp_lead, dead_lead, ratio_lead, comp_comp_lead, debris_lead]
    wins_a = sum(1 for m in metrics if m is True)
    wins_b = sum(1 for m in metrics if m is False)

    if wins_a > wins_b:
        winner, winner_wins, loser_wins = op_a, wins_a, wins_b
    elif wins_b > wins_a:
        winner, winner_wins, loser_wins = op_b, wins_b, wins_a
    else:
        winner = None
        winner_wins = loser_wins = wins_a

    sat_uri = _load_sat_image_uri()
    if sat_uri:
        st.markdown(f"""<div style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden;">
<img src="{sat_uri}" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);min-width:100%;min-height:100%;width:auto;height:auto;object-fit:cover;opacity:0.20;">
</div>""", unsafe_allow_html=True)

    html = f"""<div class="cmp-page" style="padding-top:0;position:relative;z-index:1;">

<!-- ── Profiles ── -->
<div class="cmp-profiles">
    <div class="cmp-profile">
        <p class="cmp-profile-name">{op_a}</p>
        <p class="cmp-profile-score" style="color:{tc_a};">{score_a:.1f}</p>
        <p class="cmp-profile-score-label">drcs score</p>
        <div class="cmp-profile-bar"><div class="cmp-profile-bar-fill" style="width:{min(score_a,100)}%;background:{tc_a};"></div></div>
        <span class="cmp-profile-tier" style="color:{tc_a};background:{bg_a};border:1px solid {bd_a};">{tier_a} tier</span>
    </div>
    <div class="cmp-vs-col"><span class="cmp-vs-badge">vs</span></div>
    <div class="cmp-profile">
        <p class="cmp-profile-name">{op_b}</p>
        <p class="cmp-profile-score" style="color:{tc_b};">{score_b:.1f}</p>
        <p class="cmp-profile-score-label">drcs score</p>
        <div class="cmp-profile-bar"><div class="cmp-profile-bar-fill" style="width:{min(score_b,100)}%;background:{tc_b};"></div></div>
        <span class="cmp-profile-tier" style="color:{tc_b};background:{bg_b};border:1px solid {bd_b};">{tier_b} tier</span>
    </div>
</div>

<!-- ── Comparison table ── -->
<div class="cmp-table-wrap">
<table class="cmp-table">
<thead>
<tr>
    <th class="metric-col">Metric</th>
    <th class="val-col">{op_a}</th>
    <th class="val-col">{op_b}</th>
</tr>
</thead>
<tbody>

<tr>
    <td><div class="cmp-metric"><span class="cmp-metric-icon">&#9670;</span> DRCS Reliability Score</div></td>
    <td class="cmp-cell">
        <span class="cmp-val" style="color:{tc_a};">{ar_score[0]}{score_a:.1f}</span>
        <div class="cmp-cell-bar"><div class="cmp-cell-bar-fill" style="width:{min(score_a,100)}%;background:{tc_a};"></div></div>
    </td>
    <td class="cmp-cell">
        <span class="cmp-val" style="color:{tc_b};">{ar_score[1]}{score_b:.1f}</span>
        <div class="cmp-cell-bar"><div class="cmp-cell-bar-fill" style="width:{min(score_b,100)}%;background:{tc_b};"></div></div>
    </td>
</tr>

<tr>
    <td><div class="cmp-metric"><span class="cmp-metric-icon">&#9670;</span> Reliability Tier</div></td>
    <td class="cmp-cell"><span class="cmp-badge-sm" style="color:{tc_a};background:{bg_a};border:1px solid {bd_a};">{tier_a}</span></td>
    <td class="cmp-cell"><span class="cmp-badge-sm" style="color:{tc_b};background:{bg_b};border:1px solid {bd_b};">{tier_b}</span></td>
</tr>

<tr>
    <td><div class="cmp-metric"><span class="cmp-metric-icon">&#9670;</span> Compliance Status</div></td>
    <td class="cmp-cell"><span class="cmp-badge-sm" style="color:{cc_a};background:{ccbg_a};border:1px solid {ccbd_a};">{compliant_a}</span></td>
    <td class="cmp-cell"><span class="cmp-badge-sm" style="color:{cc_b};background:{ccbg_b};border:1px solid {ccbd_b};">{compliant_b}</span></td>
</tr>

<tr>
    <td><div class="cmp-metric"><span class="cmp-metric-icon">&#9670;</span> Compliance Rate</div></td>
    <td class="cmp-cell"><span class="cmp-val">{ar_comp[0]}{comp_a:.1f}%</span></td>
    <td class="cmp-cell"><span class="cmp-val">{ar_comp[1]}{comp_b:.1f}%</span></td>
</tr>

<tr>
    <td><div class="cmp-metric"><span class="cmp-metric-icon">&#9670;</span> Compliance Component</div></td>
    <td class="cmp-cell"><span class="cmp-val">{ar_cc[0]}{comp_comp_a:.1f}</span></td>
    <td class="cmp-cell"><span class="cmp-val">{ar_cc[1]}{comp_comp_b:.1f}</span></td>
</tr>

<tr>
    <td><div class="cmp-metric"><span class="cmp-metric-icon">&#9670;</span> Debris Component</div></td>
    <td class="cmp-cell"><span class="cmp-val">{ar_deb[0]}{debris_a:.1f}</span></td>
    <td class="cmp-cell"><span class="cmp-val">{ar_deb[1]}{debris_b:.1f}</span></td>
</tr>

<tr>
    <td><div class="cmp-metric"><span class="cmp-metric-icon">&#9670;</span> Total Fleet</div></td>
    <td class="cmp-cell"><span class="cmp-val">{fleet_a:,}</span></td>
    <td class="cmp-cell"><span class="cmp-val">{fleet_b:,}</span></td>
</tr>

<tr>
    <td><div class="cmp-metric"><span class="cmp-metric-icon">&#9670;</span> Dead in Orbit</div></td>
    <td class="cmp-cell"><span class="cmp-val" style="color:{"#c94a4a" if dead_a > dead_b else "#e8e2d9"};">{ar_dead[0]}{dead_a:,}</span></td>
    <td class="cmp-cell"><span class="cmp-val" style="color:{"#c94a4a" if dead_b > dead_a else "#e8e2d9"};">{ar_dead[1]}{dead_b:,}</span></td>
</tr>

<tr>
    <td><div class="cmp-metric"><span class="cmp-metric-icon">&#9670;</span> Inactive Ratio</div></td>
    <td class="cmp-cell"><span class="cmp-val" style="color:{"#c94a4a" if ratio_a > ratio_b else "#e8e2d9"};">{ar_ratio[0]}{ratio_a:.1f}%</span></td>
    <td class="cmp-cell"><span class="cmp-val" style="color:{"#c94a4a" if ratio_b > ratio_a else "#e8e2d9"};">{ar_ratio[1]}{ratio_b:.1f}%</span></td>
</tr>

</tbody>
</table>
</div>

<!-- ── Verdict ── -->
<div class="cmp-verdict">"""

    if winner:
        html += f"""
    <p class="cmp-verdict-label">overall comparison</p>
    <p class="cmp-verdict-name">{winner}</p>
    <p class="cmp-verdict-detail">leads in {winner_wins} of 6 metrics &nbsp;·&nbsp; {loser_wins} to opponent</p>"""
    else:
        html += f"""
    <p class="cmp-verdict-label">overall comparison</p>
    <p class="cmp-verdict-tie">Even match — tied across metrics</p>
    <p class="cmp-verdict-detail">{wins_a} metrics each</p>"""

    html += """
</div>

</div>"""

    st.markdown(html, unsafe_allow_html=True)

    st.markdown("""<style>
    [data-testid="stSelectbox"] label {
        font-family: "Merriweather", serif !important;
        font-weight: 300 !important;
        font-size: 0.95rem !important;
        color: #6b6560 !important;
        letter-spacing: 0.1em !important;
    }
    [data-testid="stSelectbox"] > div > div {
        background: #161616 !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 6px !important;
        color: #e8e2d9 !important;
        font-family: "DM Mono", monospace !important;
        font-size: 1rem !important;
    }
    </style>""", unsafe_allow_html=True)
