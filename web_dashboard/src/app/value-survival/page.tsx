"use client";

import { useState } from "react";
import { Shell } from "@/components/Shell";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EChart } from "@/components/charts/EChart";
import { ChartPanel, CredibilityBanner, LoadingPulse } from "@/components/shared/Premium";
import { useDashboard } from "@/components/DashboardProvider";
import { sankeyOption, vsiBarOption } from "@/lib/charts/options";

export default function ValueSurvivalPage() {
  const { data, loading } = useDashboard();
  const rows = data?.vsi?.corridor_summary ?? [];
  const sorted = [...rows].sort((a, b) => Number(a.value_survival_index ?? 0) - Number(b.value_survival_index ?? 0));
  const sankeys = data?.visualizations?.sankey_by_corridor ?? [];
  const [idx, setIdx] = useState(0);
  const active = sankeys[idx] ?? sankeys[0];

  return (
    <Shell title="Value Survival Index" subtitle="Corridor rankings · interactive Sankey leakage decomposition" wide>
      <CredibilityBanner>
        Sankey flows decompose $100 sent into fee, FX, timing, volatility, inflation, and payout friction channels.
        Research estimates under stated assumptions.
      </CredibilityBanner>

      {loading && !data && <LoadingPulse />}

      {data && (
        <>
          <div className="grid lg:grid-cols-2 gap-4">
            <ChartPanel title="VSI ranked" caption="World Bank RPW + lab indices" badge={<Badge variant="default">BAR</Badge>}>
              <EChart
                option={vsiBarOption(
                  sorted.map((r) => String(r.corridor ?? "").slice(0, 22)),
                  sorted.map((r) => Number(r.value_survival_index ?? 0))
                )}
                height={420}
              />
            </ChartPanel>

            <ChartPanel
              title="Interactive Sankey — value leakage"
              caption={active?.corridor ?? "Select corridor"}
              badge={<Badge variant="gold">SANKEY</Badge>}
            >
              {sankeys.length > 1 && (
                <Tabs value={String(idx)} onValueChange={(v) => setIdx(Number(v))} className="mb-2">
                  <TabsList className="flex-wrap h-auto">
                    {sankeys.map((s, i) => (
                      <TabsTrigger key={i} value={String(i)} className="text-[0.62rem]">
                        {String(s.corridor ?? i).slice(0, 18)}
                      </TabsTrigger>
                    ))}
                  </TabsList>
                </Tabs>
              )}
              {active ? (
                <EChart option={sankeyOption(active)} height={380} />
              ) : (
                <p className="text-sm text-textSecondary py-8 text-center">No Sankey data in export.</p>
              )}
            </ChartPanel>
          </div>

          <ChartPanel title="Corridor detail table" caption="Full corridor summary from Python export">
            <div className="overflow-auto max-h-96 rounded-lg border border-border/50">
              <table className="w-full text-xs">
                <thead className="text-textSecondary border-b border-border bg-surfaceAlt/40 sticky top-0">
                  <tr>
                    <th className="text-left p-2.5">Corridor</th>
                    <th className="text-right p-2.5">VSI</th>
                    <th className="text-right p-2.5">Loss/$100</th>
                    <th className="text-right p-2.5">Grade</th>
                  </tr>
                </thead>
                <tbody>
                  {sorted.map((r, i) => (
                    <tr key={i} className="border-b border-border/40 hover:bg-surfaceAlt/30">
                      <td className="p-2.5">{String(r.corridor)}</td>
                      <td className="p-2.5 text-right font-mono">{Number(r.value_survival_index ?? 0).toFixed(1)}</td>
                      <td className="p-2.5 text-right font-mono">{Number(r.value_loss_usd_per_100 ?? 0).toFixed(2)}</td>
                      <td className="p-2.5 text-right">{String(r.data_quality_grade ?? "—")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ChartPanel>
        </>
      )}
    </Shell>
  );
}
