"use client";

import { Shell } from "@/components/Shell";
import { Badge } from "@/components/ui/badge";
import { EChart } from "@/components/charts/EChart";
import { AnimatedKpi, ChartPanel, CredibilityBanner, LoadingPulse } from "@/components/shared/Premium";
import { useDashboard } from "@/components/DashboardProvider";
import { lineageGraphOption } from "@/lib/charts/options";

type CatalogDataset = {
  dataset_id?: string;
  name?: string;
  layer?: string;
  path?: string;
  source_id?: string;
  frequency?: string;
  data_mode?: string;
  status?: string;
};

type CanonicalCatalog = {
  catalog_version?: string;
  product?: string;
  last_updated?: string;
  dataset_count?: number;
  active_dataset_count?: number;
  datasets_by_layer?: Record<string, number>;
  datasets?: CatalogDataset[];
  pipelines?: { pipeline_id?: string; script?: string }[];
  source_registry?: { source_count?: number; active_count?: number };
  file_counts?: { raw?: number; processed?: number; validation_reports?: number };
  latest_validation_report?: string | null;
};

function modeBadge(mode?: string) {
  if (!mode) return <Badge variant="muted">—</Badge>;
  const tone =
    mode === "live" ? "green" : mode === "mixed" ? "default" : mode === "research_starter" ? "amber" : "muted";
  return <Badge variant={tone}>{mode}</Badge>;
}

export default function DataLakePage() {
  const { data, loading } = useDashboard();
  const lake = data?.data_lake ?? {};
  const catalog = (lake.canonical_catalog ?? {}) as CanonicalCatalog;
  const lineage = data?.visualizations?.lineage_graph;
  const datasets = catalog.datasets ?? [];
  const activeCount = catalog.active_dataset_count ?? datasets.filter((d) => d.status === "active").length;

  return (
    <Shell title="Data Lake Command Center" subtitle="Canonical data-lake/ · lineage · catalog metadata" wide>
      <CredibilityBanner>
        Canonical corridor lake at <code className="text-accentCyan">data-lake/</code> (hyphen). Dataset registry
        from <code className="text-accentCyan">metadata/data_catalog.json</code>. Legacy DuckDB medallion at{" "}
        <code className="text-accentCyan">data_lake/</code> remains for VSI modules.
      </CredibilityBanner>

      {loading && !data && <LoadingPulse />}

      {data && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
            <AnimatedKpi
              label="Active datasets"
              value={String(activeCount)}
              sub={`v${catalog.catalog_version ?? "—"}`}
              tone="green"
            />
            <AnimatedKpi
              label="Raw files"
              value={String(catalog.file_counts?.raw ?? 0)}
              tone="gold"
            />
            <AnimatedKpi
              label="Processed files"
              value={String(catalog.file_counts?.processed ?? 0)}
              tone="cyan"
            />
            <AnimatedKpi
              label="Sources (active)"
              value={String(catalog.source_registry?.active_count ?? 0)}
              sub={`/${catalog.source_registry?.source_count ?? 0} registered`}
              tone="purple"
            />
            <AnimatedKpi
              label="DuckDB (legacy)"
              value={lake.duckdb_exists ? "ONLINE" : "OFF"}
              sub={String(lake.duckdb_status ?? "")}
              tone={lake.duckdb_exists ? "green" : "amber"}
            />
          </div>

          <ChartPanel
            title="Canonical catalog"
            caption={`${catalog.product ?? "USD/MXN Corridor Intelligence"} · updated ${catalog.last_updated ?? "—"}`}
            badge={<Badge variant="default">data_catalog.json</Badge>}
          >
            <div className="overflow-x-auto">
              <table className="w-full text-xs font-mono">
                <thead>
                  <tr className="text-left text-textSecondary border-b border-border/60">
                    <th className="py-2 pr-3">Dataset</th>
                    <th className="py-2 pr-3">Layer</th>
                    <th className="py-2 pr-3">Mode</th>
                    <th className="py-2 pr-3">Freq</th>
                    <th className="py-2">Path</th>
                  </tr>
                </thead>
                <tbody>
                  {datasets.map((d) => (
                    <tr key={d.dataset_id ?? d.path} className="border-b border-border/30 hover:bg-surface/40">
                      <td className="py-2 pr-3 text-textPrimary">{d.name ?? d.dataset_id}</td>
                      <td className="py-2 pr-3 uppercase text-accentCyan">{d.layer ?? "—"}</td>
                      <td className="py-2 pr-3">{modeBadge(d.data_mode)}</td>
                      <td className="py-2 pr-3">{d.frequency ?? "—"}</td>
                      <td className="py-2 text-textSecondary truncate max-w-md">{d.path ?? "—"}</td>
                    </tr>
                  ))}
                  {!datasets.length && (
                    <tr>
                      <td colSpan={5} className="py-4 text-textSecondary">
                        Run <code>npm run lake:run</code> then{" "}
                        <code>python scripts/export_dashboard_api.py</code> to populate catalog metadata.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            {catalog.pipelines?.length ? (
              <div className="mt-4 text-xs text-textSecondary space-y-1">
                <p className="uppercase tracking-wider text-textPrimary">Pipelines</p>
                {catalog.pipelines.map((p) => (
                  <p key={p.pipeline_id}>
                    <span className="text-accentCyan">{p.pipeline_id}</span> → {p.script}
                  </p>
                ))}
              </div>
            ) : null}
            {catalog.latest_validation_report ? (
              <p className="mt-3 text-xs text-textSecondary">
                Latest validation: {catalog.latest_validation_report}
              </p>
            ) : null}
          </ChartPanel>

          {lineage && (
            <ChartPanel
              title="Data lineage graph"
              caption="Drag nodes · scroll to zoom · force-directed layout"
              badge={<Badge variant="purple">GRAPH</Badge>}
            >
              <EChart option={lineageGraphOption(lineage)} height={520} />
            </ChartPanel>
          )}

          <ChartPanel title="Legacy medallion lake" caption="DuckDB sync for VSI / settlement modules">
            <div className="grid md:grid-cols-2 gap-4 text-sm text-textSecondary">
              <div className="space-y-2 font-mono text-xs">
                <p>Bronze files: {String(lake.bronze_count ?? 0)}</p>
                <p>Silver tables: {String(lake.silver_count ?? 0)}</p>
                <p>Gold outputs: {String(lake.gold_count ?? 0)}</p>
                <p>Catalog views: {String(lake.catalog_views ?? 0)}</p>
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
