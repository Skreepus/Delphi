"""
Cleans and splits SATCAT into subsets used for
labeling, scoring, and feature engineering.

Expects the standardised column names from ingestion/celestrak.py.
"""
import pandas as pd
from datetime import datetime

# Status codes that mean the satellite is dead
NON_OPERATIONAL_CODES = ["-", "D", "NONOP"]


def filter_payloads(satcat: pd.DataFrame) -> pd.DataFrame:
    """Remove debris and rocket bodies. Keep only actual satellites."""
    payloads = satcat[satcat['object_type'] == 'PAY'].copy()
    print(f"[cleaning/satcat] Payloads: {len(payloads)}")
    return payloads


def split_active(payloads: pd.DataFrame) -> pd.DataFrame:
    """Satellites still in orbit. These get scored by the risk model."""
    active = payloads[payloads['decay_date'].isna()].copy()

    now = datetime.utcnow()
    active['age_years'] = (now - active['launch_date']).dt.days / 365.25
    active['avg_altitude_km'] = (active['apogee_km'] + active['perigee_km']) / 2
    active['orbit_class'] = active['avg_altitude_km'].apply(_classify_orbit)

    print(f"[cleaning/satcat] Active in orbit: {len(active)}")
    return active


def split_dead_in_orbit(payloads: pd.DataFrame) -> pd.DataFrame:
    """Dead satellites still in orbit. Strongest non-compliance signal."""
    in_orbit = payloads[payloads['decay_date'].isna()]
    dead = in_orbit[
        in_orbit['status_code'].isin(NON_OPERATIONAL_CODES)
    ].copy()

    now = datetime.utcnow()
    dead['age_years'] = (now - dead['launch_date']).dt.days / 365.25
    dead['avg_altitude_km'] = (dead['apogee_km'] + dead['perigee_km']) / 2
    dead['orbit_class'] = dead['avg_altitude_km'].apply(_classify_orbit)

    print(f"[cleaning/satcat] Dead in orbit: {len(dead)}")
    return dead


def split_historical_decayed(payloads: pd.DataFrame) -> pd.DataFrame:
    """Satellites that already deorbited. Training data for compliance."""
    decayed = payloads[payloads['decay_date'].notna()].copy()

    decayed['time_in_orbit_years'] = (
        decayed['decay_date'] - decayed['launch_date']
    ).dt.days / 365.25

    print(f"[cleaning/satcat] Historical decayed: {len(decayed)}")
    return decayed


def build_boxscore(satcat: pd.DataFrame) -> pd.DataFrame:
    """One row per operator with counts and ratios."""
    boxscore = satcat.groupby('owner_code').agg(
        total_objects=('norad_id', 'count'),
        payloads=('object_type', lambda x: (x == 'PAY').sum()),
        rocket_bodies=('object_type', lambda x: (x == 'R/B').sum()),
        debris=('object_type', lambda x: (x == 'DEB').sum()),
        decayed=('decay_date', lambda x: x.notna().sum()),
        still_in_orbit=('decay_date', lambda x: x.isna().sum()),
    ).reset_index()

    boxscore['debris_ratio'] = (
        boxscore['debris'] / boxscore['total_objects'].clip(lower=1)
    )
    boxscore['decay_rate'] = (
        boxscore['decayed'] / boxscore['total_objects'].clip(lower=1)
    )

    print(f"[cleaning/satcat] Box score: {len(boxscore)} operators")
    return boxscore


def _classify_orbit(avg_altitude) -> str:
    if pd.isna(avg_altitude):
        return 'UNKNOWN'
    elif avg_altitude < 2000:
        return 'LEO'
    elif avg_altitude < 35286:
        return 'MEO'
    elif avg_altitude <= 36286:
        return 'GEO'
    else:
        return 'HEO'