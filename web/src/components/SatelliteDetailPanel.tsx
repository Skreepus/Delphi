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
): { label: string; dotClass: string; badgeClass: string; barColor: string } {
  if (score > th.riskHigh)
    return {
      label: "HIGH RISK",
      dotClass: "bg-red-400",
      badgeClass: "border-red-500/30 bg-red-500/[0.08] text-red-400",
      barColor: "bg-gradient-to-r from-red-500 to-red-400",
    };
  if (score > th.riskMedium)
    return {
      label: "MEDIUM RISK",
      dotClass: "bg-amber-400",
      badgeClass: "border-amber-500/30 bg-amber-500/[0.08] text-amber-300",
      barColor: "bg-gradient-to-r from-amber-500 to-amber-400",
    };
  return {
    label: "LOW RISK",
    dotClass: "bg-emerald-400",
    badgeClass: "border-emerald-500/25 bg-emerald-500/[0.08] text-emerald-400",
    barColor: "bg-gradient-to-r from-emerald-500 to-emerald-400",
  };
}

function relTierLabel(
  score: number,
  th: Pick<Th, "relLow" | "relHigh">
): { tier: string; className: string; barColor: string } {
  if (score > th.relHigh)
    return { tier: "HIGH", className: "text-delphi-accent", barColor: "bg-gradient-to-r from-delphi-accent/80 to-delphi-accent" };
  if (score >= th.relLow)
    return { tier: "MEDIUM", className: "text-amber-300/90", barColor: "bg-gradient-to-r from-amber-400/80 to-amber-300" };
  return { tier: "LOW", className: "text-rose-400/90", barColor: "bg-gradient-to-r from-rose-500/80 to-rose-400" };
}

interface Props {
  satellite: Satellite | null;
  thresholds: Th;
}

export function SatelliteDetailPanel({ satellite, thresholds }: Props) {
  if (!satellite) {
    return (
      <div className="flex h-full min-h-[180px] flex-col items-center justify-center gap-4 p-8 text-center">
        <div className="relative">
          <div className="absolute inset-0 animate-ping rounded-full bg-delphi-accent/[0.04]" style={{ animationDuration: "3s" }} />
          <div className="relative flex h-14 w-14 items-center justify-center rounded-full border border-delphi-border bg-delphi-surface">
            <svg
              className="h-6 w-6 text-delphi-muted/30"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={0.8}
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
              <line x1="2" y1="12" x2="22" y2="12" />
            </svg>
          </div>
        </div>
        <div>
          <p className="font-display text-sm tracking-wide text-delphi-muted">
            No target selected
          </p>
          <p className="mt-1.5 max-w-[180px] text-[10px] leading-relaxed text-delphi-muted/50">
            Click a satellite on the globe to inspect its risk and operator data.
          </p>
        </div>
      </div>
    );
  }

  const rb = riskBadge(satellite.satelliteRiskScore, thresholds);
  const rt = relTierLabel(satellite.operatorReliabilityScore, thresholds);
  const summary = buildRiskSummary(satellite, thresholds);

  return (
    <div className="flex max-h-[85vh] flex-col gap-3.5 overflow-y-auto p-4 text-sm font-light text-delphi-text">
      {/* Header */}
      <div className="pb-3 border-b border-delphi-border">
        <div className="flex items-start justify-between gap-2">
          <h2 className="font-display text-lg font-medium leading-tight tracking-wide text-delphi-text">
            {satellite.name}
          </h2>
          <span className={`mt-0.5 flex shrink-0 items-center gap-1.5 rounded-full border px-2 py-0.5 text-[9px] font-normal tracking-[0.15em] ${rb.badgeClass}`}>
            <span className={`h-1 w-1 rounded-full ${rb.dotClass}`} />
            {rb.label}
          </span>
        </div>
        <div className="mt-1.5 flex items-center gap-2">
          <span className="rounded-md border border-delphi-border bg-delphi-surface px-1.5 py-0.5 font-mono text-[9px] text-delphi-muted">
            {satellite.satelliteId}
          </span>
          <span className="text-[10px] tracking-wider text-delphi-muted/60">
            {satellite.orbitClass}
          </span>
        </div>
      </div>

      {/* Risk score */}
      <div className="rounded-lg border border-delphi-border bg-delphi-surface p-3.5">
        <div className="mb-2.5 flex items-center justify-between">
          <span className="text-[9px] uppercase tracking-[0.2em] text-delphi-muted/60">
            Disposal Risk Score
          </span>
        </div>
        <div className="flex items-end gap-1.5">
          <span className="font-mono text-[28px] font-light leading-none text-delphi-text">
            {satellite.satelliteRiskScore.toFixed(2)}
          </span>
          <span className="mb-1 text-[10px] text-delphi-muted/40">/ 1.00</span>
        </div>
        <div className="mt-3 h-[3px] w-full overflow-hidden rounded-full bg-delphi-border">
          <div
            className={`h-full rounded-full ${rb.barColor} transition-all duration-700 ease-out`}
            style={{ width: `${Math.min(100, satellite.satelliteRiskScore * 100)}%` }}
          />
        </div>
      </div>

      {/* Reliability */}
      <div className="rounded-lg border border-delphi-border bg-delphi-surface p-3.5">
        <div className="mb-2.5 flex items-center justify-between">
          <span className="text-[9px] uppercase tracking-[0.2em] text-delphi-muted/60">
            Operator Reliability
          </span>
          <span className={`text-[10px] font-medium tracking-wider ${rt.className}`}>
            {rt.tier}
          </span>
        </div>
        <div className="flex items-end gap-1.5">
          <span className="font-mono text-[28px] font-light leading-none text-delphi-text">
            {satellite.operatorReliabilityScore.toFixed(0)}
          </span>
          <span className="mb-1 text-[10px] text-delphi-muted/40">%</span>
        </div>
        <div className="mt-3 h-[3px] w-full overflow-hidden rounded-full bg-delphi-border">
          <div
            className={`h-full rounded-full ${rt.barColor} transition-all duration-700 ease-out`}
            style={{ width: `${Math.min(100, satellite.operatorReliabilityScore)}%` }}
          />
        </div>
      </div>

      {/* Metadata */}
      <div className="grid grid-cols-2 gap-x-3 gap-y-3 rounded-lg border border-delphi-border bg-delphi-surface p-3.5 text-[10px]">
        <div>
          <dt className="text-[8px] uppercase tracking-[0.2em] text-delphi-muted/50">Operator</dt>
          <dd className="mt-0.5 leading-snug text-delphi-text/70">{satellite.operator}</dd>
        </div>
        <div>
          <dt className="text-[8px] uppercase tracking-[0.2em] text-delphi-muted/50">Age</dt>
          <dd className="mt-0.5 font-mono text-delphi-text/70">
            {satellite.ageYears != null ? `${satellite.ageYears.toFixed(1)} yr` : "\u2014"}
          </dd>
        </div>
        <div>
          <dt className="text-[8px] uppercase tracking-[0.2em] text-delphi-muted/50">Perigee</dt>
          <dd className="mt-0.5 font-mono text-delphi-text/70">
            {satellite.perigeeKm != null ? `${satellite.perigeeKm.toFixed(0)} km` : "\u2014"}
          </dd>
        </div>
        <div>
          <dt className="text-[8px] uppercase tracking-[0.2em] text-delphi-muted/50">Apogee</dt>
          <dd className="mt-0.5 font-mono text-delphi-text/70">
            {satellite.apogeeKm != null ? `${satellite.apogeeKm.toFixed(0)} km` : "\u2014"}
          </dd>
        </div>
        <div className="col-span-2">
          <dt className="text-[8px] uppercase tracking-[0.2em] text-delphi-muted/50">Age / Lifetime</dt>
          <dd className="mt-0.5 font-mono text-delphi-text/70">
            {satellite.ageLifetimeRatio != null
              ? satellite.ageLifetimeRatio.toFixed(2)
              : "\u2014"}
          </dd>
        </div>
      </div>

      {/* Summary */}
      <div className="rounded-lg border border-delphi-border bg-delphi-surface p-3.5 text-[10px] leading-relaxed text-delphi-muted">
        {summary}
      </div>
    </div>
  );
}
