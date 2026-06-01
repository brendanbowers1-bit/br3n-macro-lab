"use client";

import { Shell } from "@/components/Shell";
import { Badge } from "@/components/ui/badge";
import { EChart } from "@/components/charts/EChart";
import { AnimatedKpi, ChartPanel, CredibilityBanner, LoadingPulse } from "@/components/shared/Premium";
import { useDashboard } from "@/components/DashboardProvider";
import { lineageGraphOption } from "@/lib/charts/options";

export default function DataLakePage() {
  const { data, loading } = useDashboard();
  const lake = data?.data_lake ?? {};
  const lineage = data?.visualizations?.lineage_graph;

  return (
    <Shell title="Data Lake Command Center" subtitle="Bronze · Silver · Gold · interactive lineage graph" wide>
      <CredibilityBanner>
        Lineage graph shows data flow from official sources through lake tiers to research modules and dashboard UI.
        DuckDB lake synced via Python — React reads exported JSON only.
      </CredibilityBanner>

      {loading && !data && <LoadingPulse />}

      {data && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <AnimatedKpi label="Bronze files" value={String(lake.bronze_count ?? 0)} tone="gold" />
            <AnimatedKpi label="Silver tables" value={String(lake.silver_count ?? 0)} tone="cyan" />
            <AnimatedKpi label="Gold outputs" value={String(lake.gold_count ?? 0)} tone="green" />
            <AnimatedKpi
              label="DuckDB"
              value={lake.duckdb_exists ? "ONLINE" : "OFF"}
              sub={String(lake.duckdb_status ?? "")}
              tone={lake.duckdb_exists ? "green" : "amber"}
            />
          </div>

          {lineage && (
            <ChartPanel
              title="Data lineage graph"
              caption="Drag nodes · scroll to zoom · force-directed layout"
              badge={<Badge variant="purple">GRAPH</Badge>}
            >
              <EChart option={lineageGraphOption(lineage)} height={520} />
            </ChartPanel>
          )}

          <ChartPanel title="Lake catalog" caption="From Python data_lake sync">
            <div className="grid md:grid-cols-2 gap-4 text-sm text-textSecondary">
              <div className="space-y-2 font-mono text-xs">
                <p>Catalog views: {String(lake.catalog_views ?? 0)}</p>
                <p>Updated: {String(lake.catalog_updated ?? "—")}</p>
                <p>DB path: {String(lake.duckdb_path ?? "run scripts/sync_data_lake.py")}</p>
              </div>
              <div className="space-y-2">
                <p className="text-xs uppercase tracking-wider text-textPrimary">Coverage by module</p>
                {Object.entries(data.coverage ?? {}).map(([mod, tables]) => (
                  <div key={mod} className="text-xs">
                    <span className="text-accentCyan uppercase">{mod}</span>:{" "}
                    {Object.entries(tables as Record<string, number | null>)
                      .map(([t, pct]) => `${t} ${pct ?? 0}% mock`)
                      .join(" · ")}
                  </div>
                ))}
              </div>
            </div>
          </ChartPanel>
        </>
      )}
    </Shell>
  );
}
