import type { DashboardPayload } from "./types";
import { withBasePath } from "./base-path";

export async function loadDashboard(): Promise<DashboardPayload | null> {
  try {
    const url = withBasePath("/api/dashboard.json");
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}
