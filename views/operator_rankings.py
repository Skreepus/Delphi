import streamlit as st
import pandas as pd
from pathlib import Path


def load_operator_data():
    """Load operator scores."""
    path = Path("data/processed/operator_scores.csv")
    if not path.exists():
        return None
    df = pd.read_csv(path)
    return df


def render():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600&family=Merriweather:wght@300;400;700&family=DM+Mono:wght@300;400&display=swap');

    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ── Page ── */
    .rankings-page {
        max-width: 1100px;
        margin: 0 auto;
        padding: 4rem 2rem;
    }
    .rankings-header {
        text-align: center;
        margin-bottom: 3.5rem;
        animation: fadeSlideUp 0.8s ease-out;
    }
    .rankings-eyebrow {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1.1rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #c9a96e;
        margin-bottom: 1.2rem;
    }
    .rankings-title {
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 3.8rem;
        color: #e8e2d9;
        margin-bottom: 1rem;
    }
    .rankings-subtitle {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1.2rem;
        color: #6b6560;
        line-height: 1.8;
    }

    /* ── Summary Bar ── */
    .summary-bar {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 4rem;
        animation: fadeSlideUp 0.8s ease-out 0.1s both;
    }
    .summary-card {
        background: rgba(22, 22, 22, 0.6);
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
    }
    .summary-num {
        font-family: "DM Mono", monospace;
        font-weight: 400;
        font-size: 2.8rem;
        color: #e8e2d9;
        margin-bottom: 0.5rem;
    }
    .summary-num.accent { color: #c9a96e; }
    .summary-num.danger { color: #c94a4a; }
    .summary-label {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.95rem;
        color: #4a4540;
        letter-spacing: 0.08em;
    }

    /* ── Top 5 Worst ── */
    .worst-section {
        margin-bottom: 4rem;
        animation: fadeSlideUp 0.8s ease-out 0.2s both;
    }
    .worst-label {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #c94a4a;
        margin-bottom: 2rem;
        text-align: center;
    }
    .worst-row {
        display: grid;
        grid-template-columns: 50px 1fr auto;
        align-items: center;
        gap: 1.2rem;
        padding: 1.3rem 1.5rem;
        margin-bottom: 0.6rem;
        background: rgba(201, 74, 74, 0.03);
        border-left: 2px solid #c94a4a;
        border-radius: 0 6px 6px 0;
        transition: all 0.3s ease;
    }
    .worst-row:hover {
        background: rgba(201, 74, 74, 0.06);
        transform: translateX(4px);
    }
    .worst-rank {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 1.05rem;
        color: #c94a4a;
        opacity: 0.6;
    }
    .worst-info {
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
    }
    .worst-name {
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 1.35rem;
        color: #e8e2d9;
    }
    .worst-bar-wrap {
        width: 100%;
        max-width: 300px;
        height: 4px;
        background: #1a1a1a;
        border-radius: 2px;
        overflow: hidden;
    }
    .worst-bar {
        height: 100%;
        background: linear-gradient(90deg, #c94a4a, #c94a4a66);
        border-radius: 2px;
    }
    .worst-meta {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.9rem;
        color: #4a4540;
    }
    .worst-score {
        font-family: "DM Mono", monospace;
        font-weight: 400;
        font-size: 1.4rem;
        color: #c94a4a;
        text-align: right;
        min-width: 60px;
    }

    /* ── Divider ── */
    .rank-divider {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 0 0 3rem 0;
    }
    .rank-divider .line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, #2a2a2a, transparent);
    }
    .rank-divider .label {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #6b6560;
        white-space: nowrap;
    }

    /* ── Tier Legend ── */
    .tier-legend {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-bottom: 2.5rem;
    }
    .tier-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .tier-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }
    .tier-dot.low { background: #c94a4a; }
    .tier-dot.medium { background: #c9a96e; }
    .tier-dot.high { background: #4a9c6e; }
    .tier-text {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.9rem;
        color: #6b6560;
    }

    /* ── Table ── */
    .rank-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 0.5rem;
    }
    .rank-table th {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.85rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #4a4540;
        text-align: left;
        padding: 0 1.2rem 1rem 1.2rem;
        border-bottom: 1px solid #1a1a1a;
    }
    .rank-table th.r { text-align: right; }
    .rank-table th.c { text-align: center; }

    .rank-row {
        background: rgba(22, 22, 22, 0.4);
        transition: all 0.3s ease;
    }
    .rank-row:hover {
        background: rgba(30, 28, 24, 0.7);
        transform: translateX(4px);
    }
    .rank-row td {
        padding: 1.1rem 1.2rem;
        border-top: 1px solid transparent;
        border-bottom: 1px solid transparent;
    }
    .rank-row td:first-child {
        border-left: 1px solid transparent;
        border-radius: 6px 0 0 6px;
    }
    .rank-row td:last-child {
        border-right: 1px solid transparent;
        border-radius: 0 6px 6px 0;
    }
    .rank-row:hover td {
        border-color: #2a2a2a;
    }

    .cell-rank {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 1rem;
        color: #4a4540;
        width: 45px;
    }
    .cell-name {
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 1.2rem;
        color: #e8e2d9;
    }
    .cell-score {
        text-align: right;
    }
    .score-val {
        font-family: "DM Mono", monospace;
        font-weight: 400;
        font-size: 1.25rem;
    }
    .s-low { color: #c94a4a; }
    .s-med { color: #c9a96e; }
    .s-high { color: #4a9c6e; }

    .cell-data {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 1.05rem;
        color: #6b6560;
        text-align: right;
    }

    .score-bar-bg {
        width: 100%;
        max-width: 120px;
        height: 4px;
        background: #1a1a1a;
        border-radius: 2px;
        overflow: hidden;
        margin-top: 4px;
    }
    .score-bar-fill {
        height: 100%;
        border-radius: 2px;
    }
    .b-low { background: linear-gradient(90deg, #c94a4a, #c94a4a55); }
    .b-med { background: linear-gradient(90deg, #c9a96e, #c9a96e55); }
    .b-high { background: linear-gradient(90deg, #4a9c6e, #4a9c6e55); }

    .tier-badge {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.8rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 3px;
        display: inline-block;
    }
    .bg-low { color: #c94a4a; background: rgba(201,74,74,0.08); border: 1px solid rgba(201,74,74,0.15); }
    .bg-med { color: #c9a96e; background: rgba(201,169,110,0.08); border: 1px solid rgba(201,169,110,0.15); }
    .bg-high { color: #4a9c6e; background: rgba(74,156,110,0.08); border: 1px solid rgba(74,156,110,0.15); }

    .table-footer {
        text-align: center;
        margin-top: 2.5rem;
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.95rem;
        color: #2a2a2a;
    }

    .rank-table-wrap {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin: 0 -0.25rem;
        padding: 0 0.25rem 0.5rem;
    }

    @media (max-width: 900px) {
        .summary-bar { grid-template-columns: 1fr 1fr !important; gap: 1rem !important; }
        .rankings-title { font-size: clamp(1.35rem, 5vw, 2.5rem) !important; line-height: 1.25 !important; }
        .rankings-subtitle { font-size: 1.05rem !important; }
    }
    @media (max-width: 560px) {
        .summary-bar { grid-template-columns: 1fr !important; }
        .tier-legend { flex-direction: column !important; gap: 0.75rem !important; align-items: center !important; }
    }
    </style>""", unsafe_allow_html=True)

    # ── Load ──
    df = load_operator_data()

    if df is None:
        st.markdown("""<div class="rankings-page">
<div class="rankings-header">
<p class="rankings-eyebrow">Rankings</p>
<p class="rankings-title">Operator Rankings</p>
<p class="rankings-subtitle">No data available. Run the scoring pipeline first.</p>
</div></div>""", unsafe_allow_html=True)
        return

    # ── Summary stats ──
    total_ops = len(df)
    high_risk = len(df[df["reliability_tier"] == "low"])
    avg_score = df["reliability_score"].mean()
    below_50 = len(df[df["reliability_score"] < 50])
    below_pct = (below_50 / total_ops * 100) if total_ops > 0 else 0

    # ── Top 5 worst ──
    worst5 = df.nsmallest(5, "reliability_score")

    worst_html = ""
    for i, (_, row) in enumerate(worst5.iterrows()):
        bar_w = min(row["reliability_score"], 100)
        fleet = int(row["total_objects"])
        dead = int(row["inactive_on_orbit"])
        worst_html += f"""<div class="worst-row">
<span class="worst-rank">{i+1:02d}</span>
<div class="worst-info">
<span class="worst-name">{row['operator_display']}</span>
<div class="worst-bar-wrap"><div class="worst-bar" style="width:{bar_w}%"></div></div>
<span class="worst-meta">fleet: {fleet}  ·  dead: {dead}</span>
</div>
<span class="worst-score">{row['reliability_score']:.1f}</span>
</div>"""

    # ── Header + Summary + Worst 5 ──
    st.markdown(f"""<div class="rankings-page">
<div class="rankings-header">
<p class="rankings-eyebrow">Operator Risk Rankings</p>
<p class="rankings-title">Ranked by DRCS reliability score. Lower score = higher risk.</p>
</div>

<div class="summary-bar">
<div class="summary-card">
<p class="summary-num">{total_ops}</p>
<p class="summary-label">operators rated</p>
</div>
<div class="summary-card">
<p class="summary-num danger">{high_risk}</p>
<p class="summary-label">high risk (low tier)</p>
</div>
<div class="summary-card">
<p class="summary-num accent">{avg_score:.1f}</p>
<p class="summary-label">average DRCS</p>
</div>
<div class="summary-card">
<p class="summary-num">{below_pct:.0f}%</p>
<p class="summary-label">score below 50</p>
</div>
</div>

<div class="worst-section">
<p class="worst-label">highest risk operators</p>
{worst_html}
</div>

<div class="rank-divider">
<div class="line"></div>
<span class="label">Full Rankings</span>
<div class="line"></div>
</div>

<div class="tier-legend">
<div class="tier-item"><div class="tier-dot low"></div><span class="tier-text">low (0-30)</span></div>
<div class="tier-item"><div class="tier-dot medium"></div><span class="tier-text">medium (30-60)</span></div>
<div class="tier-item"><div class="tier-dot high"></div><span class="tier-text">high (60-100)</span></div>
</div>

</div>""", unsafe_allow_html=True)

    # ── Filters ──
    col_tier, col_sort, col_min = st.columns([1, 1, 1])

    with col_tier:
        tier_filter = st.selectbox("Filter by tier", ["All", "Low", "Medium", "High"], key="tier_filter")

    with col_sort:
        sort_by = st.selectbox("Sort by", ["DRCS Score", "Fleet Size", "Dead in Orbit", "Compliance Rate"], key="sort_by")

    with col_min:
        min_fleet = st.slider("Minimum fleet size", min_value=1, max_value=int(df["total_objects"].max()), value=1, key="min_fleet")

    # ── Filter + Sort ──
    filtered = df.copy()
    if tier_filter != "All":
        filtered = filtered[filtered["reliability_tier"] == tier_filter.lower()]
    filtered = filtered[filtered["total_objects"] >= min_fleet]

    sort_map = {"DRCS Score": "reliability_score", "Fleet Size": "total_objects", "Dead in Orbit": "inactive_on_orbit", "Compliance Rate": "compliance_rate_smoothed"}
    ascending = True if sort_by == "DRCS Score" else False
    filtered = filtered.sort_values(sort_map[sort_by], ascending=ascending).reset_index(drop=True)

    # ── Build table ──
    rows_html = ""
    for i, row in filtered.iterrows():
        name = row["operator_display"]
        score = row["reliability_score"]
        tier = row["reliability_tier"]
        fleet = int(row["total_objects"])
        dead = int(row["inactive_on_orbit"])
        comp = row["compliance_rate_smoothed"] * 100
        bar_w = min(score, 100)

        if tier == "low":
            sc, bc, tc = "s-low", "b-low", "bg-low"
        elif tier == "medium":
            sc, bc, tc = "s-med", "b-med", "bg-med"
        else:
            sc, bc, tc = "s-high", "b-high", "bg-high"

        rows_html += f"""<tr class="rank-row">
<td class="cell-rank">{i+1:02d}</td>
<td class="cell-name">{name}</td>
<td class="cell-score"><span class="score-val {sc}">{score:.1f}</span><div class="score-bar-bg"><div class="score-bar-fill {bc}" style="width:{bar_w}%"></div></div></td>
<td style="text-align:center"><span class="tier-badge {tc}">{tier}</span></td>
<td class="cell-data">{fleet:,}</td>
<td class="cell-data">{comp:.1f}%</td>
<td class="cell-data">{dead:,}</td>
</tr>"""

    st.markdown(f"""<div class="rank-table-wrap">
<table class="rank-table">
<thead><tr>
<th></th>
<th>Operator</th>
<th class="r">DRCS</th>
<th class="c">Tier</th>
<th class="r">Fleet</th>
<th class="r">Compliance</th>
<th class="r">Dead in Orbit</th>
</tr></thead>
<tbody>{rows_html}</tbody>
</table>
</div>
<p class="table-footer">showing {len(filtered)} operators · avg DRCS {filtered['reliability_score'].mean():.1f}</p>""", unsafe_allow_html=True)

    # ── Filter widget styling ──
    st.markdown("""<style>
    [data-testid="stSelectbox"] label,
    [data-testid="stSlider"] label {
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