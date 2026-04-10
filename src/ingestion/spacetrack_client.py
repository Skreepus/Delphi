"""
Client for the Space-Track.org REST API.
https://www.space-track.org/auth/createAccount
Account has been created (Srineer)
"""
import requests
from config import SPACETRACK_BASE_URL, SPACETRACK_USERNAME, SPACETRACK_PASSWORD

SESSION_URL = f"{SPACETRACK_BASE_URL}/ajaxauth/login"
DECAY_URL = (
    f"{SPACETRACK_BASE_URL}/basicspacedata/query/class/decay"
    "/orderby/DECAY_EPOCH%20desc/limit/5000/format/json"
)


def _get_session() -> requests.Session:
    session = requests.Session()
    payload = {"identity": SPACETRACK_USERNAME, "password": SPACETRACK_PASSWORD}
    resp = session.post(SESSION_URL, data=payload)
    resp.raise_for_status()
    return session


def fetch_decay_data() -> list[dict]:
    session = _get_session()
    resp = session.get(DECAY_URL)
    resp.raise_for_status()
    data = resp.json()
    print(f"[Space-Track] Fetched {len(data):,} decay records")
    return data
