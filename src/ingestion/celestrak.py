"""
CelesTrak data ingestion.
Loads the local SATCAT CSV and standardises column names
to match the rest of the pipeline.
"""
import pandas as pd
import os

SATCAT_RENAME = {
    "OBJECT_NAME":      "satellite_name",
    "NORAD_CAT_ID":     "norad_id",
    "OBJECT_ID":        "cospar_id",
    "OBJECT_TYPE":      "object_type",
    "OPS_STATUS_CODE":  "status_code",
    "OWNER":            "owner_code",
    "LAUNCH_DATE":      "launch_date",
    "DECAY_DATE":       "decay_date",
    "PERIOD":           "period_min",
    "INCLINATION":      "inclination_deg",
    "APOGEE":           "apogee_km",
    "PERIGEE":          "perigee_km",
    "RCS":              "radar_cross_section",
    "LAUNCH_SITE":      "launch_site",
    "DATA_STATUS_CODE": "data_status_code",
    "ORBIT_CENTER":     "orbit_center",
    "ORBIT_TYPE":       "orbit_type",
}


def load_satcat(filepath: str = "data/raw/celestrak_satcat.csv") -> pd.DataFrame:
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"SATCAT file not found at {filepath}. "
            f"Download it and place it in data/raw/"
        )

    satcat = pd.read_csv(filepath)
    satcat = satcat.rename(columns=SATCAT_RENAME)
    satcat.columns = [c.strip().lower().replace(" ", "_") for c in satcat.columns]
    satcat['launch_date'] = pd.to_datetime(satcat['launch_date'], errors='coerce')
    satcat['decay_date'] = pd.to_datetime(satcat['decay_date'], errors='coerce')
    satcat['norad_id'] = pd.to_numeric(satcat['norad_id'], errors='coerce')

    print(f"[ingestion/celestrak] SATCAT loaded: {len(satcat)} rows")
    return satcat