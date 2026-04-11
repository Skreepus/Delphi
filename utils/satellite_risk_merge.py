"""
Merge satellite_risk_scores with master_satellites for enrichment and export.

Organisation name: the ``operator`` field from ``master_satellites`` takes priority
over the same column from the risk table when both exist.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow `python utils/satellite_risk_merge.py` from any working directory
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd

from config import MASTER_CSV, SATELLITE_RISK_CSV

_QUALITY_KEY_COLS = [
    "satellite_name",
    "mission_type",
    "country",
    "apogee_km",
    "perigee_km",
    "inclination_deg",
    "orbit_class",
    "launch_date",
    "expected_lifetime_yrs",
    "status_code",
]


def merge_risk_with_master(
    risk: pd.DataFrame,
    master: pd.DataFrame,
    how: str = "inner",
) -> pd.DataFrame:
    """
    Join ``risk`` to ``master`` on ``norad_id``.

    Use ``how="inner"`` (default for enriched export) to keep only satellites
    present in both tables. Use ``how="left"`` to retain all risk rows.

    For overlapping columns, coalesce: risk values first except for ``operator``,
    where the master catalogue (UCS) value is preferred, then the risk table.
    """
    overlap = [
        c
        for c in risk.columns
        if c in master.columns and c != "norad_id"
    ]
    merged = risk.merge(
        master,
        on="norad_id",
        how=how,
        suffixes=("_risk", "_master"),
    )
    for col in overlap:
        a, b = f"{col}_risk", f"{col}_master"
        if col == "operator":
            if a in merged.columns and b in merged.columns:
                merged[col] = merged[b].fillna(merged[a])
                merged = merged.drop(columns=[a, b])
            elif a in merged.columns:
                merged[col] = merged[a]
                merged = merged.drop(columns=[a])
            elif b in merged.columns:
                merged[col] = merged[b]
                merged = merged.drop(columns=[b])
            continue
        if a in merged.columns and b in merged.columns:
            merged[col] = merged[a].fillna(merged[b])
            merged = merged.drop(columns=[a, b])
        elif a in merged.columns:
            merged[col] = merged[a]
            merged = merged.drop(columns=[a])
        elif b in merged.columns:
            merged[col] = merged[b]
            merged = merged.drop(columns=[b])
    # Plain-language column for exports and UI (Australian English)
    if "operator" in merged.columns:
        merged["organisation"] = merged["operator"]
    return merged


def compute_data_quality(df: pd.DataFrame, master_ids: set | None) -> pd.DataFrame:
    """Add data_quality_score (0–1) and in_ucs_catalog."""
    out = df.copy()
    present = [c for c in _QUALITY_KEY_COLS if c in out.columns]
    if not present:
        out["data_quality_score"] = 0.0
        out["in_ucs_catalog"] = False
        return out
    base = out[present].notna().sum(axis=1) / len(present)
    if master_ids is not None and "norad_id" in out.columns:
        mids = out["norad_id"].isin(master_ids)
        out["in_ucs_catalog"] = mids
        out["data_quality_score"] = (base * 0.85 + mids.astype(float) * 0.15).clip(0, 1)
    else:
        out["data_quality_score"] = base
        out["in_ucs_catalog"] = False
    return out


def dedupe_best_per_norad(df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per ``norad_id``: keep the row with highest ``data_quality_score``,
    then ``ml_risk_score``, then ``final_risk_score``.
    """
    if df.empty or "norad_id" not in df.columns:
        return df
    sort_cols: list[str] = []
    ascending: list[bool] = []
    for col in ("data_quality_score", "ml_risk_score", "final_risk_score"):
        if col in df.columns:
            sort_cols.append(col)
            ascending.append(False)
    if sort_cols:
        ordered = df.sort_values(
            by=sort_cols,
            ascending=ascending,
            na_position="last",
        )
    else:
        ordered = df
    return ordered.drop_duplicates(subset=["norad_id"], keep="first").reset_index(
        drop=True
    )


def load_enriched_satellite_risk_from_disk() -> pd.DataFrame | None:
    """
    Load satellite_risk_scores.csv and merge master_satellites.csv when present.

    Inner-joins to catalogue rows only, scores data quality, then keeps the
    single best row per ``norad_id`` when duplicates exist.
    """
    if not SATELLITE_RISK_CSV.exists():
        return None

    risk = pd.read_csv(SATELLITE_RISK_CSV, low_memory=False)
    risk["norad_id"] = pd.to_numeric(risk["norad_id"], errors="coerce")

    master_ids: set | None = None
    if MASTER_CSV.exists():
        master = pd.read_csv(MASTER_CSV, low_memory=False)
        master["norad_id"] = pd.to_numeric(master["norad_id"], errors="coerce")
        master = master.drop_duplicates(subset=["norad_id"], keep="last")
        master_ids = set(master["norad_id"].dropna().unique())
        merged = merge_risk_with_master(risk, master, how="inner")
        out = compute_data_quality(merged, master_ids)
        return dedupe_best_per_norad(out)

    if "operator" in risk.columns and "organisation" not in risk.columns:
        risk = risk.copy()
        risk["organisation"] = risk["operator"]

    return compute_data_quality(risk, master_ids)


def export_enriched_satellite_risk_csv(
    output_path: str | os.PathLike | None = None,
) -> Path | None:
    """
    Write merged, quality-scored data to CSV (default: SATELLITE_RISK_ENRICHED_CSV).
    """
    from config import SATELLITE_RISK_ENRICHED_CSV as _DEFAULT_OUT

    df = load_enriched_satellite_risk_from_disk()
    if df is None:
        return None
    path = Path(output_path) if output_path is not None else _DEFAULT_OUT
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    out = export_enriched_satellite_risk_csv()
    if out is None:
        print(f"Missing input: {SATELLITE_RISK_CSV}")
    else:
        print(f"Wrote {out}")
