import { useCallback, useEffect, useMemo, useRef, useState } from "react";
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
  const [loading, setLoading] = useState(true);
  const [riskBand, setRiskBand] = useState<RiskBandFilter>("all");
  const [orbitClass, setOrbitClass] = useState<string>("all");
  const [operator, setOperator] = useState<string>("__all__");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onChange = () => setIsFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", onChange);
    return () => document.removeEventListener("fullscreenchange", onChange);
  }, []);

  const toggleFullscreen = useCallback(() => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      panelRef.current?.requestFullscreen().catch(() => {});
    }
  }, []);

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
      .catch((e: Error) => setLoadError(e.message))
      .finally(() => setLoading(false));
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
      if (riskBand !== "all" && bandKey(s.satelliteRiskScore, thresholds) !== riskBand)
        return false;
      if (orbitClass !== "all" && s.orbitClass.toUpperCase() !== orbitClass)
        return false;
      if (operator !== "__all__" && s.operator !== operator)
        return false;
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
    return satellites.find((s) => s.satelliteId === selectedId) ?? null;
  }, [satellites, selectedId]);

  return (
    <div ref={panelRef} className="flex h-full flex-col bg-delphi-bg font-sans text-delphi-text">
      {/* Top bar */}
      <header className="flex shrink-0 items-center justify-between border-b border-delphi-border px-5 py-2.5 bg-delphi-bg">
        <div className="flex items-center gap-3">
          <div className="flex h-7 w-7 items-center justify-center rounded-md border border-delphi-accent/20 bg-delphi-accent/[0.08]">
            <svg className="h-3.5 w-3.5 text-delphi-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <circle cx="12" cy="12" r="10" />
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
              <line x1="2" y1="12" x2="22" y2="12" />
            </svg>
          </div>
          <div>
            <span className="font-display text-base font-medium tracking-wide text-delphi-text">
              Delphi
            </span>
            <span className="ml-1.5 font-display text-base font-light italic tracking-wide text-delphi-accent">
              Explorer
            </span>
          </div>
        </div>

        {loadError && (
          <span className="rounded-md border border-red-500/20 bg-red-500/[0.08] px-2.5 py-1 text-[10px] font-light tracking-wider text-red-400/80">
            API OFFLINE
          </span>
        )}

        <div className="text-[10px] font-light uppercase tracking-[0.25em] text-delphi-muted/50">
          Space Risk Radar
        </div>
      </header>

      {/* Filter bar */}
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
        loading={loading}
        loadError={loadError}
      />

      {/* Main content */}
      <div className="flex min-h-0 flex-1 flex-col md:flex-row">
        {/* Globe */}
        <section className="relative min-h-[50vh] flex-[1.9] md:min-h-0">
          {loading && (
            <div className="absolute inset-0 z-20 flex flex-col items-center justify-center gap-4 bg-delphi-bg">
              <div className="relative">
                <div className="h-10 w-10 animate-spin rounded-full border border-transparent border-t-delphi-accent/60" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="h-2 w-2 rounded-full bg-delphi-accent/40" />
                </div>
              </div>
              <div className="text-center">
                <p className="text-[10px] font-light uppercase tracking-[0.3em] text-delphi-accent/50">
                  Loading
                </p>
                <p className="mt-1 text-[10px] font-light tracking-[0.15em] text-delphi-muted/40">
                  Acquiring orbital telemetry
                </p>
              </div>
            </div>
          )}
          <Globe
            satellites={filteredSatellites}
            selectedId={selectedId}
            onSelectSatelliteId={onSelectSatelliteId}
            isFullscreen={isFullscreen}
            onToggleFullscreen={toggleFullscreen}
          />
        </section>

        {/* Sidebar */}
        <aside className="sidebar-panel flex max-h-[50vh] w-full shrink-0 flex-col border-t border-delphi-border md:max-h-none md:w-[26%] md:min-w-[280px] md:max-w-[340px] md:border-l md:border-t-0">
          <div className="flex items-center justify-between border-b border-delphi-border px-4 py-2.5">
            <span className="text-[10px] font-light uppercase tracking-[0.25em] text-delphi-muted/60">
              Intel
            </span>
            {selectedSatellite && (
              <button
                onClick={() => setSelectedId(null)}
                className="text-[10px] font-light tracking-wider text-delphi-muted/50 transition-colors hover:text-delphi-accent"
              >
                Clear
              </button>
            )}
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
