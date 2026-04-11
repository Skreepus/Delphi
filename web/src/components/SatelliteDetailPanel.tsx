import type { Satellite } from "../types";
import { buildRiskSummary } from "../utils/riskSummary";

interface Th {
  riskHigh: number;
  riskMedium: number;
  relLow: number;
  relHigh: number;
}

function riskBadge(
  score: number,
  th: Pick<Th, "riskHigh" | "riskMedium">
): { label: string; className: string } {
  if (score > th.riskHigh)
    return { label: "High", className: "bg-red-500/20 text-red-400 border-red-500/50" };
  if (score > th.riskMedium)
    return {
      label: "Medium",
      className: "bg-amber-500/20 text-amber-300 border-amber-500/50",
    };
  return { label: "Low", className: "bg-emerald-500/20 text-emerald-400 border-emerald-500/40" };
}

function relTierLabel(
  score: number,
  th: Pick<Th, "relLow" | "relHigh">
): { tier: string; className: string } {
  if (score > th.relHigh)
    return { tier: "HIGH", className: "text-delphi-accent" };
  if (score >= th.relLow)
    return { tier: "MEDIUM", className: "text-amber-200/90" };
  return { tier: "LOW", className: "text-rose-400/90" };
}

interface Props {
  satellite: Satellite | null;
  thresholds: Th;
}

export function SatelliteDetailPanel({ satellite, thresholds }: Props) {
  if (!satellite) {
    return (
      <div className="flex h-full min-h-[120px] flex-col justify-center p-4 text-center text-sm font-light text-delphi-muted">
        <p className="font-display text-base text-delphi-accent/90">
          Select a satellite on the globe
        </p>
        <p className="mt-2 text-xs leading-relaxed text-delphi-muted">
          Points are coloured by disposal risk; size and outline reflect operator
          reliability.
        </p>
      </div>
    );
  }

  const rb = riskBadge(satellite.satelliteRiskScore, thresholds);
  const rt = relTierLabel(satellite.operatorReliabilityScore, thresholds);
  const summary = buildRiskSummary(satellite, thresholds);

  return (
    <div className="flex max-h-[85vh] flex-col gap-3 overflow-y-auto p-4 text-sm font-light text-delphi-text">
      <div>
        <h2 className="font-display text-xl font-medium tracking-wide text-delphi-text">
          {satellite.name}
        </h2>
        <p className="text-xs text-delphi-muted">NORAD {satellite.satelliteId}</p>
      </div>

      <dl className="grid grid-cols-2 gap-x-2 gap-y-2 text-xs">
        <dt className="text-delphi-muted">Operator</dt>
        <dd className="text-delphi-text">{satellite.operator}</dd>
        <dt className="text-delphi-muted">Orbit class</dt>
        <dd>{satellite.orbitClass}</dd>
        <dt className="text-delphi-muted">Perigee</dt>
        <dd>
          {satellite.perigeeKm != null ? `${satellite.perigeeKm.toFixed(0)} km` : "—"}
        </dd>
        <dt className="text-delphi-muted">Apogee</dt>
        <dd>
          {satellite.apogeeKm != null ? `${satellite.apogeeKm.toFixed(0)} km` : "—"}
        </dd>
        <dt className="text-delphi-muted">Age</dt>
        <dd>
          {satellite.ageYears != null ? `${satellite.ageYears.toFixed(1)} yr` : "—"}
        </dd>
        <dt className="text-delphi-muted">Age / lifetime</dt>
        <dd>
          {satellite.ageLifetimeRatio != null
            ? satellite.ageLifetimeRatio.toFixed(2)
            : "—"}
        </dd>
      </dl>

      <div className="rounded border border-delphi-border bg-delphi-bg/80 p-3">
        <div className="mb-1 text-[10px] font-normal uppercase tracking-[0.18em] text-delphi-muted">
          Disposal risk score
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`rounded border px-2 py-0.5 text-xs font-normal ${rb.className}`}
          >
            {rb.label}
          </span>
          <span className="text-delphi-text">
            {satellite.satelliteRiskScore.toFixed(3)}
          </span>
        </div>
      </div>

      <div className="rounded border border-delphi-border bg-delphi-bg/80 p-3">
        <div className="mb-1 text-[10px] font-normal uppercase tracking-[0.18em] text-delphi-muted">
          Operator reliability
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-medium ${rt.className}`}>{rt.tier}</span>
          <span className="text-delphi-text">
            {satellite.operatorReliabilityScore.toFixed(1)}%
          </span>
        </div>
        <p className="mt-1 text-[10px] text-delphi-muted">
          Tiers: LOW &lt; {thresholds.relLow}, MEDIUM {thresholds.relLow}–
          {thresholds.relHigh}, HIGH &gt; {thresholds.relHigh}
        </p>
      </div>

      <div className="rounded border border-delphi-border/80 bg-delphi-surface/90 p-3 text-xs leading-relaxed text-delphi-muted">
        {summary}
      </div>
    </div>
  );
}
