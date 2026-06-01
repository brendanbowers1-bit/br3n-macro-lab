import fs from "fs";
import path from "path";
import type { DashboardPayload } from "./types";

export function readDashboardSync(): DashboardPayload | null {
  try {
    const p = path.join(process.cwd(), "public", "api", "dashboard.json");
    if (!fs.existsSync(p)) return null;
    return JSON.parse(fs.readFileSync(p, "utf-8"));
  } catch {
    return null;
  }
}
