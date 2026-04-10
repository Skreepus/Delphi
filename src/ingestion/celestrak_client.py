"""
Client for CelesTrak public data.
Docs: https://celestrak.org/
"""
import requests
import pandas as pd
from io import StringIO

ACTIVE_URL = "https://celestrak.org/SOCRATES/search.php?CATNR=25544"
GP_URL = "https://celestrak.org/SOCRATES/search.php?CATNR=25544"  


def fetch_active_satellites() -> pd.DataFrame:
    """
    Fetch current active satellite GP data from CelesTrak in CSV format.

    Returns:
        DataFrame of active satellites with orbital parameters.
    """
    # TODO: Use correct CelesTrak GP endpoint for active sats
    url = "https://celestrak.org/pub/TLE/catalog.txt"  # placeholder
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    # TODO: parse TLE or CSV response depending on chosen endpoint
    raise NotImplementedError("Implement CelesTrak ingestion with chosen format (CSV/JSON/TLE)")
