import type { DashboardPayload } from "./types";

export async function loadDashboard(): Promise<DashboardPayload | null> {
  try {
    const base = typeof window !== "undefined" ? "" : process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000";
    const url = typeof window !== "undefined" ? "/api/dashboard.json" : `${base}/api/dashboard.json`;
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}
