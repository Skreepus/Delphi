"""
Label design for historical compliance classification.
"""
import pandas as pd
from config import DISPOSAL_COMPLIANCE_YEARS


def assign_historical_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign compliance labels to historical (inactive) satellites.

    Label logic (MVP):
        - compliant   → disposed/deorbited within DISPOSAL_COMPLIANCE_YEARS of mission end
        - non_compliant → inactive/dead and still in orbit beyond threshold
        - unknown     → insufficient data to determine

    Requires columns: status, mission_end_date, decay_date (or equivalent)
    """
    # TODO: map actual column names from merged dataset
    def _label(row):
        # Placeholder logic — implement once columns are confirmed
        if pd.isna(row.get("mission_end_date")):
            return "unknown"
        # ... compliance calculation
        return "unknown"

    df["compliance_label"] = df.apply(_label, axis=1)
    df["is_compliant"] = df["compliance_label"] == "compliant"
    df["is_inactive"] = df.get("status", pd.Series()).str.lower().isin(["inactive", "dead", "decayed"])
    return df
