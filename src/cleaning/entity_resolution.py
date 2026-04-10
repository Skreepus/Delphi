"""
Standardizes names in a list by finding the closest match in a reference list.
"""

import pandas as pd
from thefuzz import process

def resolve_operators(
    base_series: pd.Series,
    reference_series: pd.Series,
    threshold: int = 85,
) -> pd.Series:
    reference = reference_series.dropna().unique().tolist()

    def _match(name: str) -> str:
        if not name or name == "nan":
            return name
        result = process.extractOne(name, reference, score_cutoff=threshold)
        return result[0] if result else name

    return base_series.apply(_match)