"""
Loads the UCS Satellite Database (Excel/CSV).
Source: https://www.ucsusa.org/resources/satellite-database
"""
import pandas as pd
from pathlib import Path
from config import DATA_RAW


def load_ucs(path: Path | None = None) -> pd.DataFrame:
    """
    Read the UCS satellite Excel file into a DataFrame.

    Args:
        path: Override the default data/raw path.

    Returns:
        Raw UCS DataFrame with original column names.
    """
    file_path = path or DATA_RAW / "ucs_satellite_database.xlsx"

    if not file_path.exists():
        raise FileNotFoundError(f"UCS file not found at {file_path}. Download from UCS website.")

    # TODO: confirm sheet name matches downloaded file
    df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl")

    print(f"[UCS] Loaded {len(df):,} rows, {df.shape[1]} columns")
    return df
