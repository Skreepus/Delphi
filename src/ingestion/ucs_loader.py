"""
Loads the UCS Satellite Database (Excel).
Source: https://www.ucsusa.org/resources/satellite-database
"""
import pandas as pd
from pathlib import Path
from config import DATA_RAW


def load_ucs(path: Path | None = None) -> pd.DataFrame:
    file_path = path or DATA_RAW / "ucs_satellite_database.xlsx"

    if not file_path.exists():
        raise FileNotFoundError(f"UCS file not found at {file_path}")

    df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl")
    print(f"[UCS] Loaded {len(df):,} rows, {df.shape[1]} columns")
    return df