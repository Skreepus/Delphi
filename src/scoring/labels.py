"""
COMPLIANT:     decayed/deorbited within 25 years of mission end
NON_COMPLIANT: inactive/dead and still on orbit beyond 25yr window
UNKNOWN:       insufficient data — excluded from training

Columns needed:
    UCS:         launch_date, expected_lifetime_yrs, orbit_class
    Space-Track: decay_date, status  (joined on norad_id)
"""
import pandas as pd
from config import DISPOSAL_COMPLIANCE_YEARS


def assign_historical_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Labels each satellite as compliant, non_compliant or unknown based on whether
    it deorbited within 25 years of mission end.

    Requires decay_date joined from Space-Track on norad_id — currently unimplemented,
    all records return unknown.

    Adds:
        - compliance_label: 'compliant', 'non_compliant', or 'unknown'
        - is_compliant:     True if compliance_label == 'compliant'
        - is_inactive:      True if Space-Track status is inactive, dead or decayed
    """
    def _label(row):
        if pd.isna(row.get("launch_date")):
            return "unknown"
        # TODO: implement once decay_date is joined from Space-Track
        return "unknown"

    df["compliance_label"] = df.apply(_label, axis=1)
    df["is_compliant"] = df["compliance_label"] == "compliant"
    df["is_inactive"] = df.get("status", pd.Series(dtype=str)).str.lower().isin(
        ["inactive", "dead", "decayed"]
    )
    return df