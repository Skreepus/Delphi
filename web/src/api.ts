import type { SatellitesResponse } from "./types";

const base =
  import.meta.env.VITE_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

export async function fetchSatellites(): Promise<SatellitesResponse> {
  const r = await fetch(`${base}/api/satellites`);
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
}
