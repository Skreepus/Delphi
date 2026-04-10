"""
Merges UCS and CelesTrak data into a single master file.
UCS provides mission details. CelesTrak provides status and orbital facts.
They join on norad_id.
"""
import pandas as pd
from config import DATA_PROCESSED


def merge_datasets(
    ucs: pd.DataFrame,
    celestrak: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge UCS satellite data with CelesTrak SATCAT data.

    UCS tells you what the satellite is supposed to do.
    CelesTrak tells you what it's actually doing.

    Both must have a norad_id column.
    """
    # Only keep CelesTrak columns that UCS doesn't already have
    # to avoid duplicate fields after merge
    ucs_cols = set(ucs.columns)
    ct_keep = ['norad_id', 'status_code', 'owner_code', 'country_code',
               'decay_date', 'object_type', 'radar_cross_section']
    ct_keep = [c for c in ct_keep if c in celestrak.columns]

    # Add any orbital columns from CelesTrak that UCS is missing
    orbital_cols = ['apogee_km', 'perigee_km', 'inclination_deg', 'period_min']
    for col in orbital_cols:
        if col not in ucs_cols and col in celestrak.columns:
            ct_keep.append(col)

    ct_subset = celestrak[ct_keep].copy()

    # Merge
    master = ucs.merge(
        ct_subset,
        on='norad_id',
        how='left',
        suffixes=('', '_ct')
    )

    match_rate = master['status_code'].notna().mean()
    print(f"[merger] Merged: {len(master)} rows, match rate: {match_rate:.1%}")

    # Save
    output_path = DATA_PROCESSED / "master_satellites.parquet"
    output_path = DATA_PROCESSED / "master_satellites.csv"
    master.to_csv(output_path, index=False)
    print(f"[merger] Saved → {output_path}")
    print(f"[merger] Saved → {output_path}")

    return master