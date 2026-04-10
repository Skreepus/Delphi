"""
Data cleaning utilities for satellite dataset preprocessing.

provides functions and mappings to standardise and clean
raw satellite metadata

"""



import pandas as pd

UCS_RENAME = {
    "Name of Satellite, Alternate Names":   "satellite_name_raw",
    "Current Official Name of Satellite":   "satellite_name",
    "Country/Org of UN Registry":           "un_registry_country",
    "Country of Operator/Owner":            "country",
    "Operator/Owner":                       "operator",
    "Users":                                "users",
    "Purpose":                              "mission_type",
    "Detailed Purpose":                     "mission_type_detail",
    "Class of Orbit":                       "orbit_class",
    "Type of Orbit":                        "orbit_type",
    "Longitude of GEO (degrees)":           "geo_longitude_deg",
    "Perigee (km)":                         "perigee_km",
    "Apogee (km)":                          "apogee_km",
    "Eccentricity":                         "eccentricity",
    "Inclination (degrees)":                "inclination_deg",
    "Period (minutes)":                     "period_min",
    "Launch Mass (kg.)":                    "launch_mass_kg",
    " Dry Mass (kg.) ":                     "mass_kg",
    "Power (watts)":                        "power_watts",
    "Date of Launch":                       "launch_date",
    "Expected Lifetime (yrs.)":             "expected_lifetime_yrs",
    "Contractor":                           "contractor",
    "Country of Contractor":                "contractor_country",
    "Launch Site":                          "launch_site",
    "Launch Vehicle":                       "launch_vehicle",
    "COSPAR Number":                        "cospar_id",
    "NORAD Number":                         "norad_id",
    "Comments":                             "comments",
    "Source Used for Orbital Data":         "orbital_data_source",
}


def standardise_columns(df: pd.DataFrame, rename_map: dict) -> pd.DataFrame:
    df = df.rename(columns=rename_map)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def normalise_operator_names(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
        .str.replace(r"[^\w\s]", "", regex=True)
    )