/** @deprecated Use @/lib/types and @/lib/data instead */
export type { DashboardPayload } from "./types";
export { loadDashboard } from "./data";
export { readDashboardSync } from "./data.server";
export { C as BR3N_THEME } from "./charts/theme";
export { vsiBarOption } from "./charts/options";

export function barChartOption(
  categories: string[],
  values: number[],
  _title: string,
  _color?: string
) {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { vsiBarOption } = require("./charts/options");
  return vsiBarOption(categories, values);
}
