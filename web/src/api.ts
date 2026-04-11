import type { SatellitesResponse } from "./types";

/** Dev: default FastAPI on 8000. Production build: same-origin `/api` when VITE_API_URL is unset. */
function apiBase(): string {
  const raw = import.meta.env.VITE_API_URL;
  if (raw !== undefined && String(raw).trim() !== "") {
    return String(raw).replace(/\/$/, "");
  }
  if (import.meta.env.DEV) {
    return "http://127.0.0.1:8000";
  }
  return "";
}

export async function fetchSatellites(): Promise<SatellitesResponse> {
  const base = apiBase();
  const r = await fetch(`${base}/api/satellites`);
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
}
