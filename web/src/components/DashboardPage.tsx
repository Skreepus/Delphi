/**
 * Delphi – Space Risk Radar (single-screen dashboard)
 *
 * Plan / architecture
 * --------------------
 * - New components (this folder): `DashboardPage` (layout + data), `Globe` (Cesium),
 *   `LegendAndFilters`, `SatelliteDetailPanel`. Legacy Streamlit `app.py` is unchanged.
 * - Data flow: `fetchSatellites()` → React state (`satellites`, `thresholds`) → client-side
 *   filters produce `filteredSatellites` → passed to `Globe` for plotting; click sets
 *   `selectedId` → `SatelliteDetailPanel` resolves the row + `buildRiskSummary()`.
 * - Backend: FastAPI `GET /api/satellites` reads `data/processed/satellite_risk_enriched.csv`
 *   (same pipeline as Streamlit). No change to Python scoring code.
 *
 * Run: `uvicorn api.main:app --port 8000` from repo root, then `npm run dev` in `web/`.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchSatellites } from "../api";
import type { RiskBandFilter, Satellite } from "../types";
import { Globe } from "./Globe";
import { LegendAndFilters } from "./LegendAndFilters";
import { SatelliteDetailPanel } from "./SatelliteDetailPanel";

const DEFAULT_TH = {
  riskHigh: 0.7,
  riskMedium: 0.4,
  relLow: 40,
  relHigh: 70,
};

function bandKey(
  score: number,
  th: { riskHigh: number; riskMedium: number }
): "low" | "medium" | "high" {
  if (score > th.riskHigh) return "high";
  if (score > th.riskMedium) return "medium";
  return "low";
}

export function DashboardPage() {
  const [satellites, setSatellites] = useState<Satellite[]>([]);
  const [thresholds, setThresholds] = useState(DEFAULT_TH);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [riskBand, setRiskBand] = useState<RiskBandFilter>("all");
  const [orbitClass, setOrbitClass] = useState<string>("all");
  const [operator, setOperator] = useState<string>("__all__");
  const [selectedId, setSelectedId] = useState<number | null>(null);

  useEffect(() => {
    fetchSatellites()
      .then((res) => {
        setSatellites(res.satellites);
        if (res.thresholds) {
          setThresholds({
            riskHigh: res.thresholds.riskHigh,
            riskMedium: res.thresholds.riskMedium,
            relLow: res.thresholds.reliabilityLow,
            relHigh: res.thresholds.reliabilityHigh,
          });
        }
        if (res.warning) console.warn(res.warning);
      })
      .catch((e: Error) => setLoadError(e.message));
  }, []);

  const orbitOptions = useMemo(() => {
    const set = new Set<string>();
    for (const s of satellites) {
      if (s.orbitClass) set.add(s.orbitClass.toUpperCase());
    }
    return ["all", ...Array.from(set).sort()];
  }, [satellites]);

  const operatorOptions = useMemo(() => {
    const set = new Set<string>();
    for (const s of satellites) {
      if (s.operator) set.add(s.operator);
    }
    return ["__all__", ...Array.from(set).sort((a, b) => a.localeCompare(b))];
  }, [satellites]);

  const filteredSatellites = useMemo(() => {
    return satellites.filter((s) => {
      if (riskBand !== "all" && bandKey(s.satelliteRiskScore, thresholds) !== riskBand) {
        return false;
      }
      if (orbitClass !== "all" && s.orbitClass.toUpperCase() !== orbitClass) {
        return false;
      }
      if (operator !== "__all__" && s.operator !== operator) {
        return false;
      }
      return true;
    });
  }, [satellites, riskBand, orbitClass, operator, thresholds]);

  useEffect(() => {
    if (selectedId == null) return;
    if (!filteredSatellites.some((s) => s.satelliteId === selectedId)) {
      setSelectedId(null);
    }
  }, [filteredSatellites, selectedId]);

  const onSelectSatelliteId = useCallback((id: number | null) => {
    setSelectedId(id);
  }, []);

  const selectedSatellite = useMemo(() => {
    if (selectedId == null) return null;
    return (
      satellites.find((s) => s.satelliteId === selectedId) ?? null
    );
  }, [satellites, selectedId]);

  return (
    <div className="flex h-full flex-col bg-delphi-bg font-sans text-delphi-text">
      <header className="flex shrink-0 items-center border-b border-delphi-border bg-delphi-bg px-4 py-3 font-display tracking-wide">
        <div className="text-lg font-medium text-delphi-text md:text-xl">
          Delphi – <em className="text-delphi-accent not-italic">Space Risk Radar</em>
        </div>
        {loadError && (
          <span className="ml-4 text-xs font-light text-red-400/90">
            API: {loadError} (start `uvicorn api.main:app --port 8000`)
          </span>
        )}
      </header>

      <LegendAndFilters
        riskBand={riskBand}
        onRiskBand={setRiskBand}
        orbitClass={orbitClass}
        onOrbitClass={setOrbitClass}
        operator={operator}
        onOperator={setOperator}
        orbitOptions={orbitOptions}
        operatorOptions={operatorOptions}
        filteredCount={filteredSatellites.length}
        totalCount={satellites.length}
      />

      <div className="flex min-h-0 flex-1 flex-col md:flex-row">
        <section className="relative min-h-[45vh] flex-[1.7] md:min-h-0">
          <Globe
            satellites={filteredSatellites}
            onSelectSatelliteId={onSelectSatelliteId}
          />
        </section>

        <aside className="flex max-h-[50vh] w-full shrink-0 flex-col border-t border-delphi-border bg-delphi-surface md:max-h-none md:w-[30%] md:border-l md:border-t-0">
          <div className="border-b border-delphi-border px-3 py-2 text-[10px] font-light uppercase tracking-[0.22em] text-delphi-muted">
            Target detail
          </div>
          <SatelliteDetailPanel
            satellite={selectedSatellite}
            thresholds={thresholds}
          />
        </aside>
      </div>
    </div>
  );
}
