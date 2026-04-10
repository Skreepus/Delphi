# Orbital Credit — Methodology

## Problem Statement

Thousands of satellites orbit Earth with no standardised public-facing compliance risk score. Existing systems (Space-Track, CelesTrak) provide raw orbital data but no operator reliability context or predictive disposal risk assessment.

## What We Built

Orbital Credit merges public satellite data to compute:
1. **Operator Reliability Score** (0–100) — historical compliance rate weighted by inactive-on-orbit ratio
2. **Satellite Disposal Risk Score** (0–1) — ML model or heuristic combining orbital, lifecycle, and operator features

## Data Pipeline

1. Ingest UCS database (Excel) → `src/ingestion/ucs_loader.py`
2. Pull Space-Track decay data (API) → `src/ingestion/spacetrack_client.py`
3. (Optional) Pull CelesTrak GP data → `src/ingestion/celestrak_client.py`
4. Normalise & resolve operator entities → `src/cleaning/`
5. Merge into master satellite table → `data/processed/master_satellites.parquet`
6. Assign compliance labels → `src/scoring/labels.py`
7. Engineer features → `src/features/engineer.py`
8. Train / score → `src/models/trainer.py`, `src/scoring/satellite_risk.py`
9. Compute operator scores → `src/scoring/operator_score.py`
10. Export scored tables → `data/processed/`

## Scoring Logic

### Operator Reliability Score
```
score = compliance_rate × 60 + (1 − inactive_ratio) × 30
```
Capped 0–100. Tier: LOW (<40), MEDIUM (40–70), HIGH (>70).

### Satellite Risk Score
Gradient Boosting classifier trained on historical compliance labels.
Fallback: weighted heuristic using age/lifetime ratio + operator score + orbit class.

## Feature List

| Feature | Source |
|---------|--------|
| satellite_age_yrs | Derived from launch_date |
| age_lifetime_ratio | satellite_age / expected_lifetime |
| orbit_class | UCS |
| perigee_km / apogee_km | UCS / CelesTrak |
| mission_type | UCS |
| country | UCS |
| operator_compliance_rate | Aggregated |
| operator_inactive_on_orbit | Aggregated |
| operator_total_launched | Aggregated |

## Known Limitations (MVP)

- Entity resolution is fuzzy — some operators may be duplicated
- Compliance labels rely on disposal date proxies; true compliance requires policy interpretation
- GEO-specific disposal rules not yet implemented
- No live API integration (static data snapshots)
