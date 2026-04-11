"""
Layperson-facing satellite risk overview: minimal fields, Australian English.
Optional full-page backdrop from assets/nasa2.jpg (see README).
"""
import base64
import html
from pathlib import Path

import pandas as pd
import streamlit as st

from config import RISK_HIGH_THRESHOLD, RISK_MEDIUM_THRESHOLD
from utils.caching import load_satellite_risk_merged

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_nasa2_image_uri() -> str:
    """Data-URI for page background (empty if missing)."""
    img = _PROJECT_ROOT / "assets" / "nasa2.jpg"
    if not img.is_file():
        return ""
    b64 = base64.b64encode(img.read_bytes()).decode()
    return f"data:image/jpeg;base64,{b64}"


def _organisation_label(row: pd.Series) -> str:
    """Prefer ``organisation`` (master catalogue operator), then fallbacks."""
    for key in ("organisation", "operator", "operator_final", "owner_code"):
        v = row.get(key)
        if pd.notna(v) and str(v).strip() and str(v).lower() != "nan":
            return str(v).strip()
    return "Unknown"


def _country_label(row: pd.Series) -> str:
    v = row.get("country")
    if pd.notna(v) and str(v).strip() and str(v).lower() != "nan":
        return str(v).strip()
    return ""


def _tier_code_from_score(score: float) -> str:
    if score > RISK_HIGH_THRESHOLD:
        return "HIGH"
    if score > RISK_MEDIUM_THRESHOLD:
        return "MEDIUM"
    return "LOW"


def _concern_from_row(row: pd.Series) -> tuple[str, str, str]:
    """Badge from ML risk score when present, else combined score."""
    ml = row.get("ml_risk_score")
    if pd.notna(ml):
        t = _tier_code_from_score(float(ml))
    else:
        tier = row.get("final_risk_tier")
        score = row.get("final_risk_score")
        if pd.notna(tier) and str(tier).strip():
            t = str(tier).strip().upper()
        elif pd.notna(score):
            t = _tier_code_from_score(float(score))
        else:
            t = "LOW"

    if t == "HIGH":
        return "Higher concern", "#c94a4a", "rgba(201, 74, 74, 0.1)"
    if t == "MEDIUM":
        return "Medium concern", "#c9a96e", "rgba(201, 169, 110, 0.1)"
    return "Lower concern", "#4a9c6e", "rgba(74, 156, 110, 0.1)"


def _track_record(row: pd.Series) -> str:
    v = row.get("operator_reliability_score")
    if pd.notna(v):
        try:
            return f"{float(v):.1f}%"
        except (TypeError, ValueError):
            pass
    return ""


def _apply_sort(view: pd.DataFrame, sort_key: str) -> pd.DataFrame:
    """Return view sorted according to plain-language sort_key."""
    has_dq = "data_quality_score" in view.columns
    has_rel = "operator_reliability_score" in view.columns
    has_name = "satellite_name" in view.columns
    has_ml = "ml_risk_score" in view.columns

    def _sort_ml_then_final(ml_asc: bool):
        if not has_ml:
            if "final_risk_score" in view.columns:
                return view.sort_values(
                    by=["final_risk_score"],
                    ascending=[ml_asc],
                    na_position="last",
                )
            return view
        if "final_risk_score" in view.columns:
            return view.sort_values(
                by=["ml_risk_score", "final_risk_score"],
                ascending=[ml_asc, ml_asc],
                na_position="last",
            )
        return view.sort_values(
            by=["ml_risk_score"], ascending=[ml_asc], na_position="last"
        )

    if sort_key == "Clearest catalogue data first":
        if has_dq and has_ml:
            return view.sort_values(
                by=["data_quality_score", "ml_risk_score"],
                ascending=[False, False],
                na_position="last",
            )
        if has_dq and "final_risk_score" in view.columns:
            return view.sort_values(
                by=["data_quality_score", "final_risk_score"],
                ascending=[False, False],
                na_position="last",
            )
        if has_dq:
            return view.sort_values(
                by=["data_quality_score"], ascending=[False], na_position="last"
            )
        return _sort_ml_then_final(False)

    if sort_key == "ML risk (highest first)":
        return _sort_ml_then_final(False)

    if sort_key == "ML risk (lowest first)":
        return _sort_ml_then_final(True)

    if sort_key == "Organisation track record (best first)" and has_rel:
        return view.sort_values(
            by=["operator_reliability_score"],
            ascending=[False],
            na_position="last",
        )

    if sort_key == "Organisation track record (lowest first)" and has_rel:
        return view.sort_values(
            by=["operator_reliability_score"],
            ascending=[True],
            na_position="last",
        )

    if sort_key == "Name (A to Z)" and has_name:
        name_key = view["satellite_name"].fillna("").astype(str)
        return view.assign(_sort_name=name_key).sort_values(
            by=["_sort_name"], ascending=[True], na_position="last"
        ).drop(columns=["_sort_name"])

    if sort_key == "Name (Z to A)" and has_name:
        name_key = view["satellite_name"].fillna("").astype(str)
        return view.assign(_sort_name=name_key).sort_values(
            by=["_sort_name"], ascending=[False], na_position="last"
        ).drop(columns=["_sort_name"])

    return view


def render():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600&family=Merriweather:wght@300;400;700&display=swap');
.lay-wrap { max-width: min(960px, 100%); margin: 0 auto; padding: clamp(1.25rem, 4vw, 2rem) clamp(1rem, 3vw, 1.5rem) 3rem; box-sizing: border-box; position: relative; z-index: 1; }
.lay-card {
    background: rgba(22, 22, 22, 0.75);
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 1.35rem 1.5rem 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s ease;
    position: relative;
    z-index: 1;
}
.lay-card:hover { border-color: #3a3a3a; }
.lay-card-title {
    font-family: "Lora", serif; font-weight: 500; font-size: 1.35rem; color: #e8e2d9;
    margin: 0 0 0.75rem 0; line-height: 1.3;
}
.lay-badge {
    display: inline-block; font-family: "Merriweather", serif; font-size: 0.8rem;
    letter-spacing: 0.06em; padding: 0.35rem 0.75rem; border-radius: 6px; margin-bottom: 0.85rem;
}
.lay-line {
    font-family: "Merriweather", serif; font-weight: 300; font-size: 0.95rem;
    color: #a39e94; line-height: 1.65; margin: 0.25rem 0;
}
.lay-line strong { color: #c9a96e; font-weight: 500; }
.lay-foot {
    font-family: "Merriweather", serif; font-size: 0.82rem; color: #5c574e;
    margin-top: 0.9rem; line-height: 1.55; font-style: italic;
}
.lay-empty {
    text-align: center; font-family: "Merriweather", serif; color: #6b6560;
    padding: 3rem 1rem;
    position: relative;
    z-index: 1;
}
</style>
""",
        unsafe_allow_html=True,
    )

    nasa_uri = _load_nasa2_image_uri()
    if nasa_uri:
        st.markdown(
            f"""<div style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden;">
<img src="{nasa_uri}" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);min-width:100%;min-height:100%;width:auto;height:auto;object-fit:cover;opacity:0.20;">
</div>""",
            unsafe_allow_html=True,
        )

    df = load_satellite_risk_merged()

    if df is None or len(df) == 0:
        st.markdown(
            '<div class="lay-wrap"><p class="lay-empty">No scored satellite data yet. '
            "Run the data and modelling pipeline first.</p></div>",
            unsafe_allow_html=True,
        )
        return

    if "final_risk_tier" in df.columns:
        df["final_risk_tier"] = df["final_risk_tier"].astype(str).str.strip().str.upper()

    sort_choices = [
        "Clearest catalogue data first",
        "ML risk (highest first)",
        "ML risk (lowest first)",
        "Organisation track record (best first)",
        "Organisation track record (lowest first)",
        "Name (A to Z)",
        "Name (Z to A)",
    ]
    if "operator_reliability_score" not in df.columns:
        sort_choices = [
            c
            for c in sort_choices
            if not c.startswith("Organisation track record")
        ]

    row1_col1, row1_col2 = st.columns([1.2, 1], gap="large")
    with row1_col1:
        q = st.text_input(
            "Search by name or organisation",
            key="lay_search",
            placeholder="Type part of a name…",
        )
    with row1_col2:
        sort_by = st.selectbox(
            "Sort by",
            options=sort_choices,
            index=0,
            key="lay_sort",
            help="Choose how to order satellites before limiting how many are shown.",
        )

    n_show = st.slider("How many to show", 5, 60, 18, key="lay_count")

    view = df.copy()
    if q:
        ql = q.lower()
        mask = pd.Series(False, index=view.index)
        for col in (
            "satellite_name",
            "organisation",
            "operator_final",
            "operator",
            "country",
        ):
            if col in view.columns:
                mask |= view[col].astype(str).str.lower().str.contains(ql, na=False)
        view = view[mask]

    view = _apply_sort(view, sort_by)
    view = view.head(n_show)

    if len(view) == 0:
        st.markdown(
            '<p class="lay-empty">No satellites match your search.</p>',
            unsafe_allow_html=True,
        )
        return

    for _, row in view.iterrows():
        name = row.get("satellite_name")
        if pd.isna(name) or str(name).strip() == "" or str(name).lower() == "nan":
            title = "Unnamed object"
        else:
            title = str(name).strip()

        concern, accent, bg = _concern_from_row(row)
        org = html.escape(_organisation_label(row))
        country = _country_label(row)
        country_h = html.escape(country) if country else ""

        tr = _track_record(row)
        ml = row.get("ml_risk_score")
        ml_s = f"{float(ml):.2f}" if pd.notna(ml) else "—"
        ml_note = (
            ""
            if pd.notna(ml)
            else '<p class="lay-line"><em>Risk score not available for this row; badge uses the combined score.</em></p>'
        )

        country_line = (
            f'<p class="lay-line"><strong>Country</strong> — {country_h}</p>'
            if country_h
            else ""
        )
        tr_line = (
            f'<p class="lay-line"><strong>Organisation track record</strong> — {html.escape(tr)} '
            "estimated from historical compliance patterns in our data.</p>"
            if tr
            else ""
        )

        st.markdown(
            f"""<div class="lay-card">
<span class="lay-badge" style="color:{accent};background:{bg};border:1px solid {accent}33;">{html.escape(concern)}</span>
<p class="lay-card-title">{html.escape(title)}</p>
<p class="lay-line"><strong>Organisation</strong> — {org}</p>
{country_line}
<p class="lay-line"><strong>Risk score</strong> — {ml_s} (0 = lower, 1 = higher)</p>
{ml_note}
{tr_line}
<p class="lay-foot">Scores combine orbit, age, and operator history. They are uncertain by nature.</p>
</div>""",
            unsafe_allow_html=True,
        )
