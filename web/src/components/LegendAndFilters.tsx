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
  loading: boolean;
  loadError: string | null;
}

function PillButton({
  active,
  onClick,
  children,
  color,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
  color?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full border px-2.5 py-1 text-[10px] font-light uppercase tracking-[0.12em] transition-all duration-200
        ${active
          ? `border-transparent ${color ?? "bg-delphi-surface text-delphi-text"}`
          : "border-delphi-border bg-transparent text-delphi-muted/60 hover:border-delphi-border hover:text-delphi-muted"
        }`}
    >
      {children}
    </button>
  );
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
  loading,
}: Props) {
  const selectClass =
    "appearance-none rounded-md border border-delphi-border bg-delphi-surface px-2.5 py-1.5 text-[10px] tracking-wider text-delphi-muted transition-all duration-200 focus:border-delphi-accent/40 focus:outline-none focus:ring-1 focus:ring-delphi-accent/20 cursor-pointer hover:border-delphi-accent/20 hover:text-delphi-text";

  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 border-b border-delphi-border bg-delphi-bg px-5 py-2 text-[11px] font-light">
      {/* Risk pill filters */}
      <div className="flex items-center gap-1.5">
        <span className="mr-1 text-[9px] uppercase tracking-[0.2em] text-delphi-muted/50">
          Risk
        </span>
        <PillButton active={riskBand === "all"} onClick={() => onRiskBand("all")}>
          All
        </PillButton>
        <PillButton
          active={riskBand === "low"}
          onClick={() => onRiskBand("low")}
          color="bg-emerald-500/15 text-emerald-400"
        >
          Low
        </PillButton>
        <PillButton
          active={riskBand === "medium"}
          onClick={() => onRiskBand("medium")}
          color="bg-amber-500/15 text-amber-300"
        >
          Med
        </PillButton>
        <PillButton
          active={riskBand === "high"}
          onClick={() => onRiskBand("high")}
          color="bg-red-500/15 text-red-400"
        >
          High
        </PillButton>
      </div>

      {/* Divider */}
      <div className="h-4 w-px bg-delphi-border" />

      {/* Dropdowns */}
      <div className="flex items-center gap-2">
        <label className="text-[9px] uppercase tracking-[0.15em] text-delphi-muted/50">
          Orbit
        </label>
        <select
          value={orbitClass}
          onChange={(e) => onOrbitClass(e.target.value)}
          className={selectClass}
        >
          {orbitOptions.map((o) => (
            <option key={o} value={o}>
              {o === "all" ? "All orbits" : o}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-2">
        <label className="text-[9px] uppercase tracking-[0.15em] text-delphi-muted/50">
          Operator
        </label>
        <select
          value={operator}
          onChange={(e) => onOperator(e.target.value)}
          className={`max-w-[160px] ${selectClass}`}
        >
          {operatorOptions.map((o) => (
            <option key={o} value={o}>
              {o === "__all__" ? "All operators" : o}
            </option>
          ))}
        </select>
      </div>

      {/* Count */}
      <div className="ml-auto flex items-center gap-2">
        <div className="flex items-center gap-1.5 text-[10px] tracking-wider text-delphi-muted/50">
          {loading ? (
            <span className="animate-pulse text-delphi-accent/40">Scanning...</span>
          ) : (
            <>
              <span className="font-mono text-delphi-accent/70">
                {filteredCount.toLocaleString()}
              </span>
              <span className="text-delphi-muted/30">/</span>
              <span className="font-mono text-delphi-muted/50">{totalCount.toLocaleString()}</span>
              <span className="text-delphi-muted/40">tracked</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
