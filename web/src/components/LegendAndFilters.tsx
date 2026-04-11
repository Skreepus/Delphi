import type { RiskBandFilter } from "../types";

interface Props {
  riskBand: RiskBandFilter;
  onRiskBand: (v: RiskBandFilter) => void;
  orbitClass: string;
  onOrbitClass: (v: string) => void;
  operator: string;
  onOperator: (v: string) => void;
  orbitOptions: string[];
  operatorOptions: string[];
  filteredCount: number;
  totalCount: number;
}

export function LegendAndFilters({
  riskBand,
  onRiskBand,
  orbitClass,
  onOrbitClass,
  operator,
  onOperator,
  orbitOptions,
  operatorOptions,
  filteredCount,
  totalCount,
}: Props) {
  const selectClass =
    "rounded border border-delphi-border bg-delphi-surface px-2 py-1.5 text-sm text-delphi-text focus:border-delphi-accent focus:outline-none focus:ring-1 focus:ring-delphi-accent/40";

  return (
    <div className="flex flex-wrap items-end gap-4 border-b border-delphi-border bg-delphi-bg px-4 py-3 text-xs font-light text-delphi-text">
      <div className="flex flex-wrap gap-3">
        <span className="text-[10px] uppercase tracking-[0.22em] text-delphi-accent">
          Legend
        </span>
        <span className="flex items-center gap-1.5 text-delphi-muted">
          <span className="h-2 w-4 rounded-sm bg-gradient-to-r from-emerald-600 to-red-600" />
          Colour → disposal risk (0–1)
        </span>
        <span className="flex items-center gap-1.5 text-delphi-muted">
          <span className="inline-block h-2 w-2 rounded-full border-2 border-delphi-text/50" />
          Size / outline → operator reliability
        </span>
      </div>

      <div className="ml-auto flex flex-wrap items-center gap-2">
        <label className="text-delphi-muted">Risk</label>
        <select
          value={riskBand}
          onChange={(e) => onRiskBand(e.target.value as RiskBandFilter)}
          className={selectClass}
        >
          <option value="all">All</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>

        <label className="text-delphi-muted">Orbit</label>
        <select
          value={orbitClass}
          onChange={(e) => onOrbitClass(e.target.value)}
          className={selectClass}
        >
          {orbitOptions.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>

        <label className="text-delphi-muted">Operator</label>
        <select
          value={operator}
          onChange={(e) => onOperator(e.target.value)}
          className={`max-w-[200px] ${selectClass}`}
        >
          {operatorOptions.map((o) => (
            <option key={o} value={o}>
              {o === "__all__" ? "All" : o}
            </option>
          ))}
        </select>

        <span className="text-delphi-muted">
          Showing{" "}
          <span className="font-normal text-delphi-accent">{filteredCount}</span> /{" "}
          {totalCount}
        </span>
      </div>
    </div>
  );
}
