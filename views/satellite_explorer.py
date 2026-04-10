import streamlit as st
import pandas as pd
from pathlib import Path


def load_satellite_data():
    """Load satellite risk scores."""
    path = Path("data/processed/satellite_risk_scores.csv")
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
    .explorer-page {
        max-width: 1100px;
        margin: 0 auto;
        padding: 4rem 2rem;
    }
    .explorer-header {
        text-align: center;
        margin-bottom: 3.5rem;
        animation: fadeSlideUp 0.8s ease-out;
    }
    .explorer-eyebrow {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1.1rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #c9a96e;
        margin-bottom: 1.2rem;
    }
    .explorer-title {
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 3.8rem;
        color: #e8e2d9;
        margin-bottom: 1rem;
    }
    .explorer-subtitle {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1.2rem;
        color: #6b6560;
        line-height: 1.8;
    }

    /* ── Summary Bar ── */
    .exp-summary-bar {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 4rem;
        animation: fadeSlideUp 0.8s ease-out 0.1s both;
    }
    .exp-summary-card {
        background: rgba(22, 22, 22, 0.6);
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
    }
    .exp-summary-num {
        font-family: "DM Mono", monospace;
        font-weight: 400;
        font-size: 2.8rem;
        color: #e8e2d9;
        margin-bottom: 0.5rem;
    }
    .exp-summary-num.accent { color: #c9a96e; }
    .exp-summary-num.danger { color: #c94a4a; }
    .exp-summary-num.safe { color: #4a9c6e; }
    .exp-summary-label {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.95rem;
        color: #4a4540;
        letter-spacing: 0.08em;
    }

    /* ── Risk Distribution ── */
    .risk-dist-section {
        margin-bottom: 4rem;
        animation: fadeSlideUp 0.8s ease-out 0.15s both;
    }
    .risk-dist-title {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #6b6560;
        margin-bottom: 2rem;
        text-align: center;
    }
    .risk-dist-bars {
        display: flex;
        align-items: flex-end;
        justify-content: center;
        gap: 3px;
        height: 180px;
        padding: 0 2rem;
        margin-bottom: 1rem;
    }
    .risk-dist-bar {
        flex: 1;
        max-width: 28px;
        border-radius: 3px 3px 0 0;
        transition: all 0.3s ease;
        cursor: default;
        position: relative;
    }
    .risk-dist-bar:hover {
        opacity: 0.8;
        transform: scaleY(1.03);
        transform-origin: bottom;
    }
    .risk-dist-axis {
        display: flex;
        justify-content: space-between;
        padding: 0 2rem;
    }
    .risk-dist-axis span {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.75rem;
        color: #4a4540;
    }
    .risk-dist-legend {
        display: flex;
        justify-content: center;
        gap: 2.5rem;
        margin-top: 1.5rem;
    }
    .risk-dist-legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .risk-dist-legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }
    .risk-dist-legend-text {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.85rem;
        color: #6b6560;
    }

    /* ── Top 10 Highest Risk ── */
    .spotlight-section {
        margin-bottom: 4rem;
        animation: fadeSlideUp 0.8s ease-out 0.2s both;
    }
    .spotlight-label {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #c94a4a;
        margin-bottom: 2rem;
        text-align: center;
    }
    .spotlight-row {
        display: grid;
        grid-template-columns: 50px 1fr auto auto;
        align-items: center;
        gap: 1.2rem;
        padding: 1.3rem 1.5rem;
        margin-bottom: 0.6rem;
        background: rgba(201, 74, 74, 0.03);
        border-left: 2px solid #c94a4a;
        border-radius: 0 6px 6px 0;
        transition: all 0.3s ease;
    }
    .spotlight-row:hover {
        background: rgba(201, 74, 74, 0.06);
        transform: translateX(4px);
    }
    .spotlight-rank {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 1.05rem;
        color: #c94a4a;
        opacity: 0.6;
    }
    .spotlight-info {
        display: flex;
        flex-direction: column;
        gap: 0.3rem;
    }
    .spotlight-name {
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 1.3rem;
        color: #e8e2d9;
    }
    .spotlight-meta {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.8rem;
        color: #4a4540;
    }
    .spotlight-bar-wrap {
        width: 120px;
        height: 4px;
        background: #1a1a1a;
        border-radius: 2px;
        overflow: hidden;
    }
    .spotlight-bar {
        height: 100%;
        background: linear-gradient(90deg, #c94a4a, #c94a4a66);
        border-radius: 2px;
    }
    .spotlight-score {
        font-family: "DM Mono", monospace;
        font-weight: 400;
        font-size: 1.4rem;
        color: #c94a4a;
        text-align: right;
        min-width: 55px;
    }

    /* ── Orbit Class Breakdown ── */
    .orbit-breakdown {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 4rem;
        animation: fadeSlideUp 0.8s ease-out 0.25s both;
    }
    .orbit-card {
        background: rgba(22, 22, 22, 0.6);
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .orbit-card:hover {
        border-color: #3a3a3a;
        transform: translateY(-2px);
    }
    .orbit-card-label {
        font-family: "DM Mono", monospace;
        font-weight: 400;
        font-size: 1rem;
        letter-spacing: 0.1em;
        color: #c9a96e;
        margin-bottom: 1rem;
    }
    .orbit-card-num {
        font-family: "DM Mono", monospace;
        font-weight: 400;
        font-size: 2.2rem;
        color: #e8e2d9;
        margin-bottom: 0.3rem;
    }
    .orbit-card-sub {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.8rem;
        color: #4a4540;
    }
    .orbit-card-risk {
        margin-top: 1rem;
        font-family: "DM Mono", monospace;
        font-weight: 400;
        font-size: 1.1rem;
    }
    .orbit-card-risk.risk-high { color: #c94a4a; }
    .orbit-card-risk.risk-med { color: #c9a96e; }
    .orbit-card-risk.risk-low { color: #4a9c6e; }
    .orbit-card-risk-label {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 0.75rem;
        color: #4a4540;
        margin-top: 0.2rem;
    }

    /* ── Divider ── */
    .exp-divider {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 0 0 3rem 0;
    }
    .exp-divider .line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, #2a2a2a, transparent);
    }
    .exp-divider .label {
        font-family: "Merriweather", serif;
        font-weight: 300;
        font-size: 1rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #6b6560;
        white-space: nowrap;
    }

    /* ── Tier Legend ── */
    .exp-tier-legend {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-bottom: 2.5rem;
    }
    .exp-tier-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .exp-tier-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }
    .exp-tier-dot.low { background: #4a9c6e; }
    .exp-tier-dot.medium { background: #c9a96e; }
    .exp-tier-dot.high { background: #c94a4a; }
    .exp-tier-text {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.9rem;
        color: #6b6560;
    }

    /* ── Table ── */
    .sat-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 0.5rem;
    }
    .sat-table th {
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
    .sat-table th.r { text-align: right; }
    .sat-table th.c { text-align: center; }

    .sat-row {
        background: rgba(22, 22, 22, 0.4);
        transition: all 0.3s ease;
    }
    .sat-row:hover {
        background: rgba(30, 28, 24, 0.7);
        transform: translateX(4px);
    }
    .sat-row td {
        padding: 1.1rem 1.2rem;
        border-top: 1px solid transparent;
        border-bottom: 1px solid transparent;
    }
    .sat-row td:first-child {
        border-left: 1px solid transparent;
        border-radius: 6px 0 0 6px;
    }
    .sat-row td:last-child {
        border-right: 1px solid transparent;
        border-radius: 0 6px 6px 0;
    }
    .sat-row:hover td {
        border-color: #2a2a2a;
    }

    .sat-cell-rank {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 1rem;
        color: #4a4540;
        width: 45px;
    }
    .sat-cell-name {
        font-family: "Lora", serif;
        font-weight: 500;
        font-size: 1.1rem;
        color: #e8e2d9;
    }
    .sat-cell-name-sub {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.75rem;
        color: #4a4540;
        margin-top: 2px;
    }
    .sat-cell-score {
        text-align: right;
    }
    .sat-score-val {
        font-family: "DM Mono", monospace;
        font-weight: 400;
        font-size: 1.2rem;
    }
    .sat-s-high { color: #c94a4a; }
    .sat-s-med { color: #c9a96e; }
    .sat-s-low { color: #4a9c6e; }

    .sat-cell-data {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 1rem;
        color: #6b6560;
        text-align: right;
    }
    .sat-cell-data-center {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 1rem;
        color: #6b6560;
        text-align: center;
    }

    .sat-score-bar-bg {
        width: 100%;
        max-width: 100px;
        height: 4px;
        background: #1a1a1a;
        border-radius: 2px;
        overflow: hidden;
        margin-top: 4px;
    }
    .sat-score-bar-fill {
        height: 100%;
        border-radius: 2px;
    }
    .sat-b-high { background: linear-gradient(90deg, #c94a4a, #c94a4a55); }
    .sat-b-med { background: linear-gradient(90deg, #c9a96e, #c9a96e55); }
    .sat-b-low { background: linear-gradient(90deg, #4a9c6e, #4a9c6e55); }

    .sat-tier-badge {
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.8rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 3px;
        display: inline-block;
    }
    .sat-bg-high { color: #c94a4a; background: rgba(201,74,74,0.08); border: 1px solid rgba(201,74,74,0.15); }
    .sat-bg-med { color: #c9a96e; background: rgba(201,169,110,0.08); border: 1px solid rgba(201,169,110,0.15); }
    .sat-bg-low { color: #4a9c6e; background: rgba(74,156,110,0.08); border: 1px solid rgba(74,156,110,0.15); }

    .sat-table-footer {
        text-align: center;
        margin-top: 2.5rem;
        font-family: "DM Mono", monospace;
        font-weight: 300;
        font-size: 0.95rem;
        color: #2a2a2a;
    }

    /* ── Search box styling ── */
    .search-section {
        margin-bottom: 2rem;
    }
    </style>""", unsafe_allow_html=True)

    # ── Load ──
    df = load_satellite_data()

    if df is None:
        st.markdown("""<div class="explorer-page">
<div class="explorer-header">
<p class="explorer-eyebrow">Satellite Explorer</p>
<p class="explorer-title">Satellite Risk Scores</p>
<p class="explorer-subtitle">No data available. Run the scoring pipeline first.</p>
</div></div>""", unsafe_allow_html=True)
        return

    # ── Normalize tier column ──
    df["final_risk_tier"] = df["final_risk_tier"].str.strip().str.upper()

    # ── Summary stats ──
    total_sats = len(df)
    high_risk_count = len(df[df["final_risk_tier"] == "HIGH"])
    med_risk_count = len(df[df["final_risk_tier"] == "MEDIUM"])
    low_risk_count = len(df[df["final_risk_tier"] == "LOW"])
    avg_risk = df["final_risk_score"].mean()

    # ── Risk distribution histogram data ──
    bins = 20
    hist_min, hist_max = 0.0, 1.0
    bin_edges = [hist_min + i * (hist_max - hist_min) / bins for i in range(bins + 1)]
    hist_counts = []
    hist_colors = []
    for i in range(bins):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        if i == bins - 1:
            count = len(df[(df["final_risk_score"] >= lo) & (df["final_risk_score"] <= hi)])
        else:
            count = len(df[(df["final_risk_score"] >= lo) & (df["final_risk_score"] < hi)])
        hist_counts.append(count)
        mid = (lo + hi) / 2
        if mid < 0.3:
            hist_colors.append("#4a9c6e")
        elif mid < 0.6:
            hist_colors.append("#c9a96e")
        else:
            hist_colors.append("#c94a4a")

    max_count = max(hist_counts) if max(hist_counts) > 0 else 1
    hist_bars_html = ""
    for i in range(bins):
        h = max(int((hist_counts[i] / max_count) * 160), 2) if hist_counts[i] > 0 else 2
        hist_bars_html += f'<div class="risk-dist-bar" style="height:{h}px;background:{hist_colors[i]};" title="{hist_counts[i]:,} satellites"></div>'

    # ── Top 10 highest risk ──
    top10 = df.nsmallest(10, "ml_compliance_probability") if "ml_compliance_probability" in df.columns else df.nlargest(10, "final_risk_score")

    spotlight_html = ""
    for i, (_, row) in enumerate(top10.iterrows()):
        name = row.get("satellite_name", "Unknown")
        score = row["final_risk_score"]
        bar_w = min(score * 100, 100)
        orbit = row.get("orbit_class", "—")
        owner = row.get("owner_code", "—")
        age = row.get("age_years", None)
        age_str = f"{age:.1f}y" if pd.notna(age) else "—"

        spotlight_html += f"""<div class="spotlight-row">
<span class="spotlight-rank">{i+1:02d}</span>
<div class="spotlight-info">
<span class="spotlight-name">{name}</span>
<span class="spotlight-meta">{owner} · {orbit} · age: {age_str}</span>
</div>
<div class="spotlight-bar-wrap"><div class="spotlight-bar" style="width:{bar_w}%"></div></div>
<span class="spotlight-score">{score:.3f}</span>
</div>"""

    # ── Orbit class breakdown ──
    orbit_html = ""
    if "orbit_class" in df.columns:
        orbit_classes = ["LEO", "MEO", "GEO"]
        for oc in orbit_classes:
            subset = df[df["orbit_class"] == oc]
            count = len(subset)
            if count > 0:
                avg_r = subset["final_risk_score"].mean()
                high_pct = len(subset[subset["final_risk_tier"] == "HIGH"]) / count * 100
                if avg_r >= 0.6:
                    risk_class = "risk-high"
                elif avg_r >= 0.3:
                    risk_class = "risk-med"
                else:
                    risk_class = "risk-low"
                orbit_html += f"""<div class="orbit-card">
<p class="orbit-card-label">{oc}</p>
<p class="orbit-card-num">{count:,}</p>
<p class="orbit-card-sub">satellites</p>
<p class="orbit-card-risk {risk_class}">{avg_r:.3f}</p>
<p class="orbit-card-risk-label">avg risk score</p>
<p class="orbit-card-sub" style="margin-top:0.5rem">{high_pct:.1f}% high risk</p>
</div>"""

    # ── Header + Summary + Distribution + Spotlight + Orbit ──
    st.markdown(f"""<div class="explorer-page">

<div class="explorer-header">
<p class="explorer-eyebrow">Satellite Intelligence</p>
<p class="explorer-title">Satellite Risk Explorer</p>
<p class="explorer-subtitle">Every tracked satellite, scored by our ML model. Higher score = higher risk.</p>
</div>

<div class="exp-summary-bar">
<div class="exp-summary-card">
<p class="exp-summary-num">{total_sats:,}</p>
<p class="exp-summary-label">satellites scored</p>
</div>
<div class="exp-summary-card">
<p class="exp-summary-num danger">{high_risk_count:,}</p>
<p class="exp-summary-label">high risk</p>
</div>
<div class="exp-summary-card">
<p class="exp-summary-num accent">{med_risk_count:,}</p>
<p class="exp-summary-label">medium risk</p>
</div>
<div class="exp-summary-card">
<p class="exp-summary-num safe">{low_risk_count:,}</p>
<p class="exp-summary-label">low risk</p>
</div>
</div>

<div class="risk-dist-section">
<p class="risk-dist-title">Risk Score Distribution</p>
<div class="risk-dist-bars">{hist_bars_html}</div>
<div class="risk-dist-axis">
<span>0.0 — low risk</span>
<span>0.5</span>
<span>1.0 — high risk</span>
</div>
<div class="risk-dist-legend">
<div class="risk-dist-legend-item"><div class="risk-dist-legend-dot" style="background:#4a9c6e"></div><span class="risk-dist-legend-text">low (&lt;0.3)</span></div>
<div class="risk-dist-legend-item"><div class="risk-dist-legend-dot" style="background:#c9a96e"></div><span class="risk-dist-legend-text">medium (0.3–0.6)</span></div>
<div class="risk-dist-legend-item"><div class="risk-dist-legend-dot" style="background:#c94a4a"></div><span class="risk-dist-legend-text">high (&gt;0.6)</span></div>
</div>
</div>

<div class="spotlight-section">
<p class="spotlight-label">10 highest risk satellites</p>
{spotlight_html}
</div>

{"<div class='orbit-breakdown'>" + orbit_html + "</div>" if orbit_html else ""}

<div class="exp-divider">
<div class="line"></div>
<span class="label">Full Satellite Database</span>
<div class="line"></div>
</div>

<div class="exp-tier-legend">
<div class="exp-tier-item"><div class="exp-tier-dot high"></div><span class="exp-tier-text">high risk (&gt;0.6)</span></div>
<div class="exp-tier-item"><div class="exp-tier-dot medium"></div><span class="exp-tier-text">medium (0.3–0.6)</span></div>
<div class="exp-tier-item"><div class="exp-tier-dot low"></div><span class="exp-tier-text">low (&lt;0.3)</span></div>
</div>

</div>""", unsafe_allow_html=True)

    # ── Search ──
    search = st.text_input("Search satellites by name, COSPAR ID, or operator", key="sat_search", placeholder="e.g. STARLINK, 2020-001A, spacex...")

    # ── Filters ──
    col_tier, col_orbit, col_status, col_sort = st.columns([1, 1, 1, 1])

    tier_options = ["All", "High", "Medium", "Low"]
    with col_tier:
        tier_filter = st.selectbox("Risk tier", tier_options, key="sat_tier")

    orbit_options = ["All"]
    if "orbit_class" in df.columns:
        orbit_options += sorted(df["orbit_class"].dropna().unique().tolist())
    with col_orbit:
        orbit_filter = st.selectbox("Orbit class", orbit_options, key="sat_orbit")

    status_options = ["All", "Active", "Inactive"]
    with col_status:
        status_filter = st.selectbox("Status", status_options, key="sat_status")

    with col_sort:
        sort_by = st.selectbox("Sort by", ["Risk Score (High→Low)", "Risk Score (Low→High)", "Age (Oldest)", "Age (Newest)", "ML Probability"], key="sat_sort")

    # ── Apply filters ──
    filtered = df.copy()

    if search:
        q = search.lower()
        mask = pd.Series([False] * len(filtered))
        if "satellite_name" in filtered.columns:
            mask |= filtered["satellite_name"].astype(str).str.lower().str.contains(q, na=False)
        if "cospar_id" in filtered.columns:
            mask |= filtered["cospar_id"].astype(str).str.lower().str.contains(q, na=False)
        if "operator_final" in filtered.columns:
            mask |= filtered["operator_final"].astype(str).str.lower().str.contains(q, na=False)
        if "owner_code" in filtered.columns:
            mask |= filtered["owner_code"].astype(str).str.lower().str.contains(q, na=False)
        filtered = filtered[mask]

    if tier_filter != "All":
        filtered = filtered[filtered["final_risk_tier"] == tier_filter.upper()]

    if orbit_filter != "All" and "orbit_class" in filtered.columns:
        filtered = filtered[filtered["orbit_class"] == orbit_filter]

    if status_filter != "All" and "is_inactive" in filtered.columns:
        if status_filter == "Active":
            filtered = filtered[filtered["is_inactive"] == False]
        else:
            filtered = filtered[filtered["is_inactive"] == True]

    sort_map = {
        "Risk Score (High→Low)": ("final_risk_score", False),
        "Risk Score (Low→High)": ("final_risk_score", True),
        "Age (Oldest)": ("age_years", False),
        "Age (Newest)": ("age_years", True),
        "ML Probability": ("ml_compliance_probability", True),
    }
    sort_col, sort_asc = sort_map[sort_by]
    if sort_col in filtered.columns:
        filtered = filtered.sort_values(sort_col, ascending=sort_asc, na_position="last").reset_index(drop=True)

    # ── Pagination ──
    per_page = 50
    total_pages = max(1, (len(filtered) + per_page - 1) // per_page)

    page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1, key="sat_page")
    start_idx = (page_num - 1) * per_page
    page_df = filtered.iloc[start_idx:start_idx + per_page]

    # ── Build table ──
    rows_html = ""
    for i, (_, row) in enumerate(page_df.iterrows()):
        rank = start_idx + i + 1
        name = row.get("satellite_name", "Unknown")
        cospar = row.get("cospar_id", "—")
        score = row["final_risk_score"]
        tier = row["final_risk_tier"]
        ml_prob = row.get("ml_compliance_probability", None)
        ml_str = f"{ml_prob:.2f}" if pd.notna(ml_prob) else "—"
        orbit = row.get("orbit_class", "—")
        age = row.get("age_years", None)
        age_str = f"{age:.1f}" if pd.notna(age) else "—"
        owner = row.get("owner_code", "—")
        bar_w = min(score * 100, 100)

        if tier == "HIGH":
            sc, bc, tc = "sat-s-high", "sat-b-high", "sat-bg-high"
        elif tier == "MEDIUM":
            sc, bc, tc = "sat-s-med", "sat-b-med", "sat-bg-med"
        else:
            sc, bc, tc = "sat-s-low", "sat-b-low", "sat-bg-low"

        rows_html += f"""<tr class="sat-row">
<td class="sat-cell-rank">{rank:02d}</td>
<td><div class="sat-cell-name">{name}</div><div class="sat-cell-name-sub">{cospar} · {owner}</div></td>
<td class="sat-cell-score"><span class="sat-score-val {sc}">{score:.3f}</span><div class="sat-score-bar-bg"><div class="sat-score-bar-fill {bc}" style="width:{bar_w}%"></div></div></td>
<td style="text-align:center"><span class="sat-tier-badge {tc}">{tier}</span></td>
<td class="sat-cell-data">{ml_str}</td>
<td class="sat-cell-data-center">{orbit if orbit and orbit != "nan" else "—"}</td>
<td class="sat-cell-data">{age_str}</td>
</tr>"""

    st.markdown(f"""<table class="sat-table">
<thead><tr>
<th></th>
<th>Satellite</th>
<th class="r">Risk Score</th>
<th class="c">Tier</th>
<th class="r">ML Prob</th>
<th class="c">Orbit</th>
<th class="r">Age (yrs)</th>
</tr></thead>
<tbody>{rows_html}</tbody>
</table>
<p class="sat-table-footer">page {page_num} of {total_pages} · {len(filtered):,} satellites match filters · avg risk {filtered['final_risk_score'].mean():.3f}</p>""", unsafe_allow_html=True)

    # ── Filter widget styling ──
    st.markdown("""<style>
    [data-testid="stTextInput"] label,
    [data-testid="stSelectbox"] label,
    [data-testid="stNumberInput"] label {
        font-family: "Merriweather", serif !important;
        font-weight: 300 !important;
        font-size: 0.95rem !important;
        color: #6b6560 !important;
        letter-spacing: 0.1em !important;
    }
    [data-testid="stTextInput"] > div > div > input {
        background: #161616 !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 6px !important;
        color: #e8e2d9 !important;
        font-family: "DM Mono", monospace !important;
        font-size: 1rem !important;
        padding: 0.7rem 1rem !important;
    }
    [data-testid="stTextInput"] > div > div > input:focus {
        border-color: #c9a96e !important;
        box-shadow: 0 0 0 1px #c9a96e33 !important;
    }
    [data-testid="stTextInput"] > div > div > input::placeholder {
        color: #3a3a3a !important;
    }
    [data-testid="stSelectbox"] > div > div {
        background: #161616 !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 6px !important;
        color: #e8e2d9 !important;
        font-family: "DM Mono", monospace !important;
        font-size: 1rem !important;
    }
    [data-testid="stNumberInput"] > div > div > input {
        background: #161616 !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 6px !important;
        color: #e8e2d9 !important;
        font-family: "DM Mono", monospace !important;
        font-size: 1rem !important;
    }
    </style>""", unsafe_allow_html=True)