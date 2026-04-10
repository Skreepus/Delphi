from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

NUMERIC_FEATURES = [
    "satellite_age_yrs",
    "expected_lifetime_yrs",
    "age_lifetime_ratio",
    "perigee_km",
    "apogee_km",
    "inclination_deg",
    "period_min",
    "launch_mass_kg",
    "mass_kg",
    "power_watts",
    "operator_total_launched",
    "operator_inactive_on_orbit",
    "operator_compliance_rate",
]

CATEGORICAL_FEATURES = [
    "orbit_class",
    "orbit_type",
    "mission_type",
    "users",
    "country",
]


def build_preprocessor() -> ColumnTransformer:
    """
    Creates a data processing pipeline to prepare satellite data for machine learning.

    This tool handles two types of data:
    1. Numeric: Fills missing values with the median and scales them to a standard range.
    2. Categorical: Fills missing values and converts text labels into numbers (One-Hot Encoding).

    Returns:
        ColumnTransformer: A configured scikit-learn preprocessor ready to fit and transform data.
    """
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("num", numeric_pipe, NUMERIC_FEATURES),
        ("cat", categorical_pipe, CATEGORICAL_FEATURES),
    ])