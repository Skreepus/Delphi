# Delphi — Methodology

## Problem statement

Public orbital catalogues (CelesTrak, Space-Track, UCS) expose trajectories and metadata, but they do not provide a single, transparent **operator reliability** index or **per-satellite disposal-risk** estimate that combines catalogue fields with historical compliance behaviour. Delphi is an MVP that closes part of that gap using reproducible rules and a simple supervised model.

---

## Data sources

| Source | Role in Delphi |
|--------|----------------|
| **UCS Satellite Database** (`ucs_satellite_database.xlsx`) | Operator names, mission type, country, orbit parameters, expected lifetime where available |
| **CelesTrak SATCAT** (`satcat.csv`) | NORAD IDs, payload vs debris, status, owner codes — full catalogue coverage |
| **Space-Track decay** (`spacetrack_decay.csv`, optional) | Decay epochs and metadata merged onto master rows by `norad_id` |

`run_pipeline.py` standardises UCS columns, fuzzy-matches operator names (`src/cleaning/entity_resolution.py`), merges UCS with SATCAT payloads, then left-joins Space-Track fields. Outputs live in `data/processed/` (CSV).

---

## Compliance labelling

Implementation: `src/scoring/labels.py`, driven by `DISPOSAL_COMPLIANCE_YEARS` in `config.py` (default **5 years**, aligned with FCC post-mission disposal guidance).

- **`compliant`** — Object decayed within the compliance window after estimated mission end.
- **`non_compliant`** — Late decay or still inconsistent with the rule where data supports a call.
- **`unknown`** — Active satellites, insufficient lifetime data, or inside the compliance window (these rows are **prediction targets** for the ML path, not training labels).

The pipeline labels the full SATCAT universe by enriching splits with UCS-backed lifetimes where possible and using conservative fallbacks for SATCAT-only rows (see module docstring in `labels.py`).

---

## Operator reliability (DRCS score)

Implementation: `src/scoring/operator_reliability.py`, configuration in `config.py`.

**Composite (0–100, higher is better):**

- `compliance_component` = Bayesian-smoothed compliance rate × `COMPLIANCE_WEIGHT` (default **70**)
- `debris_component` = (1 − inactive_on_orbit_ratio) × `DEBRIS_WEIGHT` (default **30**)
- **`reliability_score`** = `compliance_component + debris_component` (clamped to 0–100)

**Bayesian smoothing** reduces variance for small fleets: smoothed rate = `(compliant + m × g) / (total + m)` with `m = MIN_OPERATOR_HISTORY` (default 3) and `g` = global compliance rate.

**Reliability tiers** (UI “tier” for operators):

| Tier | Score range |
|------|-------------|
| High | ≥ 70 |
| Medium | 40–69 |
| Low | < 40 |

**Operator identity:** Rows are grouped on a resolved operator column (`operator_final`), preferring UCS-resolved names and falling back to SATCAT `owner_code` when needed (`operator_source` tracks provenance).

Exported file: **`data/processed/operator_scores.csv`**.

---

## Feature table (for ML)

Implementation: `src/features/feature_engineering.py`.

Built from `labeled_satellites.csv` with age, orbital numerics, lifetime presence flag, and **operator reliability** joined from `operator_scores.csv`. Numeric features used by the model are listed in `NUMERIC_FEATURES` (e.g. `age_years`, apogee/perigee, inclination, period, `operator_reliability_score`, `has_lifetime_data`). Missing values are filled with the training median.

Output: **`data/processed/feature_table.csv`**.

---

## Satellite risk — logistic regression model

Implementation: `src/models/compliance_risk_model.py`.

1. Restrict training to rows with `compliance_label` ∈ {`compliant`, `non_compliant`}.
2. **Z-score** each feature on the training split: \(z = (x - \mu) / \sigma\).
3. Fit **logistic regression** (`sklearn.linear_model.LogisticRegression`) to predict **P(compliant)**.
4. Define **`ml_risk_score` = 1 − P(compliant)** for labelled training rows and for **unknown** (active) prediction rows.
5. Set **`final_risk_score`** = `ml_risk_score`, with missing values filled by **0.5** before tiering; **`final_risk_tier`** uses the same 0.4 / 0.7 cutoffs as `config.py`.

**Tier thresholds** (config `RISK_MEDIUM_THRESHOLD`, `RISK_HIGH_THRESHOLD`, defaults **0.4** / **0.7**):

- **LOW** — score &lt; 0.4  
- **MEDIUM** — 0.4 ≤ score &lt; 0.7  
- **HIGH** — score ≥ 0.7  

Model coefficients, normalisation parameters, and evaluation JSON are written under **`data/models/`**. Scored satellites are saved to **`satellite_risk_scores.csv`**.

---

## Satellite risk — heuristic baseline

Implementation: `src/scoring/risk_categories.py` (`compute_heuristic_risk`).

Rule-based score in \([0, 1]\):

\[
\text{risk} = 0.5 \times \text{age\_factor} + 0.3 \times \text{operator\_factor} + 0.2 \times \text{geo\_factor}
\]

- **Age factor** — From `age_lifetime_ratio` (capped); missing lifetime → moderate default.
- **Operator factor** — `1 - (\text{reliability\_score} / 100)` (inverted so weak operators increase risk).
- **Geo factor** — Elevated for **GEO** (long orbital residence; passive decay negligible).

Same 0.4 / 0.7 tier cutoffs apply when tiers are derived from this score. This path is useful when you want CSV outputs without training sklearn.

---

## Enriched satellite table

**`utils/satellite_risk_merge.py`** inner-joins `satellite_risk_scores.csv` to `master_satellites.csv` on `norad_id`, prefers UCS **operator** naming, deduplicates, and adds **data_quality_score** from catalogue completeness. Export: **`satellite_risk_enriched.csv`**, consumed by Streamlit overview/explorer and `api/main.py`.

---

## Dashboard mapping

| View | Module | Primary data |
|------|--------|----------------|
| Home | `views/home.py` | Hero + static headline stats (optional `stars.mp4`) |
| Compare | `views/operator_compare.py` | `operator_scores.csv`, backdrop `assets/sat1.jpg` |
| Rankings | `views/operator_rankings.py` | `operator_scores.csv`, backdrop `assets/nasa1.jpg` |
| Explorer | `views/explorer.py` | Iframe to radar UI + API (`DELPHI_RADAR_URL`) |
| Overview | `views/satellite_overview_lay.py` | Enriched risk merge, backdrop `assets/nasa2.jpg` |
| About | `views/about.py` | Static content |

---

## Known limitations (MVP)

- Scores depend on **catalogue freshness** and **labelling assumptions**; UCS lifetime and operator fields are incomplete for many objects.
- **Operator** for SATCAT-only rows is proxied by **owner code**, not company name.
- The logistic model is intentionally **simple** (linear in z-scored features); it is an interpretable baseline, not a production orbital safety certification.
- Historical compliance rules are a **simplified** reading of regulatory disposal expectations and do not constitute legal advice.
