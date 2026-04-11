export interface Satellite {
  satelliteId: number;
  name: string;
  operator: string;
  orbitClass: string;
  perigeeKm: number | null;
  apogeeKm: number | null;
  ageYears: number | null;
  ageLifetimeRatio: number | null;
  satelliteRiskScore: number;
  operatorReliabilityScore: number;
  latitude: number;
  longitude: number;
  altitudeMeters: number;
}

export interface ApiThresholds {
  riskHigh: number;
  riskMedium: number;
  reliabilityLow: number;
  reliabilityHigh: number;
}

export interface SatellitesResponse {
  satellites: Satellite[];
  warning?: string;
  thresholds?: ApiThresholds;
}

export type RiskBandFilter = "all" | "low" | "medium" | "high";
