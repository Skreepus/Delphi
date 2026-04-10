"""
Merges UCS, Space-Track, and CelesTrak data into a single master file 
and saves it as a .parquet file.
"""

import pandas as pd
from config import DATA_PROCESSED


def merge_datasets(
    ucs: pd.DataFrame,
    spacetrack: pd.DataFrame,
    celestrak: pd.DataFrame | None = None,
) -> pd.DataFrame:
    master = ucs.copy()

    # Join Space-Track decay data on norad_id
    # master = master.merge(spacetrack, on="norad_id", how="left")

    # Join CelesTrak orbital data on norad_id (optional)
    # if celestrak is not None:
    #     master = master.merge(celestrak, on="norad_id", how="left")

    output_path = DATA_PROCESSED / "master_satellites.parquet"
    master.to_parquet(output_path, index=False)
    print(f"[Merger] Saved {len(master):,} rows → {output_path}")
    return master