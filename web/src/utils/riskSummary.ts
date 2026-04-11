import type { Satellite } from "../types";

const DEFAULT_TH = { riskHigh: 0.7, riskMedium: 0.4, relLow: 40, relHigh: 70 };

function riskBand(
  score: number,
  th: { riskHigh: number; riskMedium: number }
): "high" | "medium" | "low" {
  if (score > th.riskHigh) return "high";
  if (score > th.riskMedium) return "medium";
  return "low";
}

function relTier(
  score: number,
  th: { relLow: number; relHigh: number }
): "HIGH" | "MEDIUM" | "LOW" {
  if (score > th.relHigh) return "HIGH";
  if (score >= th.relLow) return "MEDIUM";
  return "LOW";
}

/**
 * Deterministic, template-based explanation from metrics (no external AI).
 */
export function buildRiskSummary(
  s: Satellite,
  thresholds: { riskHigh: number; riskMedium: number; relLow: number; relHigh: number } = DEFAULT_TH
): string {
  const band = riskBand(s.satelliteRiskScore, thresholds);
  const opTier = relTier(s.operatorReliabilityScore, {
    relLow: thresholds.relLow,
    relHigh: thresholds.relHigh,
  });

  const reasons: string[] = [];

  if (s.ageLifetimeRatio != null && s.ageLifetimeRatio > 1) {
    reasons.push("its age exceeds the design lifetime on record");
  } else if (s.ageLifetimeRatio != null && s.ageLifetimeRatio > 0.85) {
    reasons.push("it is approaching the end of its design lifetime");
  }

  if (opTier === "LOW") {
    reasons.push("the operator shows a low historical reliability score in our data");
  } else if (opTier === "MEDIUM") {
    reasons.push("the operator has only a moderate reliability score");
  }

  const oc = (s.orbitClass || "").toUpperCase();
  if (oc === "LEO" && s.satelliteRiskScore > thresholds.riskMedium) {
    reasons.push("it sits in low Earth orbit where traffic and debris risk are elevated");
  }
  if (oc === "GEO" || oc === "HEO" || oc === "GTO") {
    reasons.push("its high-altitude orbit implies long orbital lifetimes and different disposal constraints");
  }

  if (s.perigeeKm != null && s.apogeeKm != null) {
    const spread = Math.abs(s.apogeeKm - s.perigeeKm);
    if (spread > 5000) {
      reasons.push("the orbit is highly elliptical, which can complicate end-of-life planning");
    }
  }

  if (reasons.length === 0) {
    if (band === "high") {
      return `This satellite is assessed as high disposal-risk (score ${s.satelliteRiskScore.toFixed(2)}) given its orbit, age, and operator context in our model.`;
    }
    if (band === "medium") {
      return `This satellite shows medium disposal-risk (score ${s.satelliteRiskScore.toFixed(2)}) relative to the fleet.`;
    }
    return `This satellite shows lower modelled disposal-risk (score ${s.satelliteRiskScore.toFixed(2)}) with operator reliability ${s.operatorReliabilityScore.toFixed(0)}%.`;
  }

  const bandLabel =
    band === "high" ? "high" : band === "medium" ? "medium" : "lower";

  return `This satellite is ${bandLabel} disposal-risk because ${reasons.join(", ")}.`;
}
