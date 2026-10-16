import type { Incident } from "../types";

export async function getIncidents(): Promise<Incident[]> {
  const response = await fetch("/api/v1/incidents");
  if (!response.ok) throw new Error(`Incident API returned ${response.status}`);
  return response.json() as Promise<Incident[]>;
}
