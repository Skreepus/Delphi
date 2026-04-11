"""
Delphi JSON API for the Space Risk Radar web UI.

Serves satellite metrics from ``satellite_risk_enriched.csv`` (same pipeline as Streamlit).

Run: uvicorn api.main:app --reload --port 8000
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Project root (parent of api/)
ROOT = Path(__file__).resolve().parent.parent
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import RISK_HIGH_THRESHOLD, RISK_MEDIUM_THRESHOLD, SATELLITE_RISK_ENRICHED_CSV

_DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "http://localhost:8502",
    "http://127.0.0.1:8502",
    "http://localhost:8503",
    "http://127.0.0.1:8503",
]


def _cors_allow_origins() -> list[str]:
    extra = os.getenv("DELPHI_CORS_ORIGINS", "")
    out = list(_DEFAULT_CORS_ORIGINS)
    for part in extra.split(","):
        o = part.strip()
        if o and o not in out:
            out.append(o)
    return out


app = FastAPI(title="Delphi Space Risk API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _viz_position(
    norad: int,
    inclination_deg: float | None,
    apogee_km: float | None,
    perigee_km: float | None,
    geo_lon_deg: float | None,
) -> tuple[float, float, float]:
    """
    Approximate lat/lon/alt for globe plotting. Positions are deterministic but not
    propagated from TLEs (visualisation only).
    """
    ap = float(apogee_km) if apogee_km is not None and not pd.isna(apogee_km) else 400.0
    pe = float(perigee_km) if perigee_km is not None and not pd.isna(perigee_km) else 400.0
    alt_m = max(200_000.0, (ap + pe) / 2.0 * 1000.0)

    if geo_lon_deg is not None and not pd.isna(geo_lon_deg):
        lon = float(geo_lon_deg)
        if lon > 180:
            lon -= 360
    else:
        lon = ((norad * 137) % 360) - 180

    inc = float(inclination_deg) if inclination_deg is not None and not pd.isna(inclination_deg) else 51.6
    lat = math.sin(norad * 0.017453292) * min(abs(inc), 85.0) * 0.92
    lat = max(-85.0, min(85.0, lat))
    return lat, lon, alt_m


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/media/stars.mp4")
def hero_background_stars():
    """
    Serve the homepage background loop with correct video/mp4 headers.
    Streamlit cannot host .mp4 via its static folder; base64 in markdown also fails for large files.
    """
    path = ROOT / "assets" / "stars.mp4"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Place assets/stars.mp4 in the project root.")
    return FileResponse(
        path,
        media_type="video/mp4",
        filename="stars.mp4",
    )


@app.get("/api/satellites")
def list_satellites():
    """Return all enriched satellites as JSON for the radar UI."""
    path = SATELLITE_RISK_ENRICHED_CSV
    if not path.exists():
        return {"satellites": [], "warning": f"Missing data file: {path}"}

    df = pd.read_csv(path, low_memory=False)
    out = []

    for _, row in df.iterrows():
        try:
            norad = int(float(row.get("norad_id")))
        except (TypeError, ValueError):
            continue

        el = row.get("expected_lifetime_yrs")
        age = row.get("age_years")
        age_ratio = None
        if el is not None and not pd.isna(el) and float(el) > 0 and age is not None and not pd.isna(age):
            age_ratio = float(age) / float(el)

        risk = row.get("ml_risk_score")
        if risk is None or pd.isna(risk):
            risk = row.get("final_risk_score")
        if risk is None or pd.isna(risk):
            risk = 0.5
        else:
            risk = float(risk)

        rel = row.get("operator_reliability_score")
        if rel is None or pd.isna(rel):
            rel = 50.0
        else:
            rel = float(rel)

        op = row.get("organisation") or row.get("operator_final") or row.get("operator") or "Unknown"
        name = row.get("satellite_name") or row.get("satellite_name_raw") or f"NORAD {norad}"
        oc = row.get("orbit_class") or row.get("orbit_type") or "Other"
        if isinstance(oc, str) and oc.strip():
            orbit_class = oc.strip().upper()
        else:
            orbit_class = "OTHER"

        pe = row.get("perigee_km")
        ap = row.get("apogee_km")
        ag = row.get("age_years")
        geo_lon = row.get("geo_longitude_deg")
        inc = row.get("inclination_deg")

        lat, lon, alt_m = _viz_position(
            norad,
            float(inc) if inc is not None and not pd.isna(inc) else None,
            float(ap) if ap is not None and not pd.isna(ap) else None,
            float(pe) if pe is not None and not pd.isna(pe) else None,
            float(geo_lon) if geo_lon is not None and not pd.isna(geo_lon) else None,
        )

        out.append(
            {
                "satelliteId": norad,
                "name": str(name),
                "operator": str(op),
                "orbitClass": orbit_class,
                "perigeeKm": float(pe) if pe is not None and not pd.isna(pe) else None,
                "apogeeKm": float(ap) if ap is not None and not pd.isna(ap) else None,
                "ageYears": float(ag) if ag is not None and not pd.isna(ag) else None,
                "ageLifetimeRatio": age_ratio,
                "satelliteRiskScore": risk,
                "operatorReliabilityScore": rel,
                "latitude": lat,
                "longitude": lon,
                "altitudeMeters": alt_m,
            }
        )

    return {
        "satellites": out,
        "thresholds": {
            "riskHigh": RISK_HIGH_THRESHOLD,
            "riskMedium": RISK_MEDIUM_THRESHOLD,
            "reliabilityLow": 40,
            "reliabilityHigh": 70,
        },
    }
