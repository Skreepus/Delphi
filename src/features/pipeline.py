"""
Feature list definitions.

Kept as a separate file so both feature_engineering.py and
compliance_model.py can import the same lists.

No sklearn. Just lists of column names.
"""

from src.features.feature_engineering import (
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    METADATA_COLUMNS,
)