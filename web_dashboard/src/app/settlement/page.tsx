"use client";

import { Shell } from "@/components/Shell";
import { Badge } from "@/components/ui/badge";
import { EChart } from "@/components/charts/EChart";
import { SettlementTimelineAnimator } from "@/components/charts/SettlementTimeline";
import { AnimatedKpi, ChartPanel, CredibilityBanner, LoadingPulse } from "@/components/shared/Premium";
import { useDashboard } from "@/components/DashboardProvider";
import { C } from "@/lib/charts/theme";

export default function SettlementPage() {
  const { data, loading } = useDashboard();
  const sdi = data?.settlement?.settlement_drag ?? [];
  const sorted = [...sdi]
    .sort((a, b) => Number(a.settlement_drag_index ?? 0) - Number(b.settlement_drag_index ?? 0))
    .slice(0, 15);
  const timeline = data?.visualizations?.settlement_timeline ?? [];

  return (
    <Shell title="Settlement Economics" subtitle="Settlement drag · animated finality timeline" wide>
      <CredibilityBanner>
        Settlement timeline stages derived from finality quality index in Python export. SDI ranks entities by drag proxy in this research spec.
      </CredibilityBanner>

      {loading && !data && <LoadingPulse />}

      {data && (
        <>
          <div className="grid lg:grid-cols-2 gap-4">
            <ChartPanel title="Settlement Drag Index" caption="Lower SDI = higher drag proxy" badge={<Badge variant="gold">SDI</Badge>}>
              <EChart
                option={{
                  backgroundColor: "transparent",
                  grid: { left: 120, right: 24, top: 24, bottom: 24 },
                  xAxis: { type: "value", axisLabel: { color: C.muted }, splitLine: { lineStyle: { color: C.border } } },
                  yAxis: {
                    type: "category",
                    data: sorted.map((r) => String(r.entity ?? "").slice(0, 40)),
                    axisLabel: { color: C.muted, fontSize: 9 },
                  },
                  series: [{
                    type: "bar",
                    data: sorted.map((r) => Number(r.settlement_drag_index ?? 0)),
                    itemStyle: { color: C.gold, borderRadius: [0, 3, 3, 0] },
                  }],
                  tooltip: { trigger: "axis" },
                }}
                height={440}
              />
            </ChartPanel>

            <ChartPanel
              title="Settlement timeline animation"
              caption="Finality ladder — cumulative hours vs score"
              badge={<Badge variant="default">TIMELINE</Badge>}
            >
              <SettlementTimelineAnimator stages={timeline} />
            </ChartPanel>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <AnimatedKpi label="Settlement tables" value={String(Object.keys(data.settlement).length)} sub="In export" tone="cyan" />
            <AnimatedKpi label="SDI rows" value={String(sdi.length)} tone="gold" />
            <AnimatedKpi label="Timeline stages" value={String(timeline.length)} tone="purple" />
            <AnimatedKpi label="Worst entity" value={String(data.executive?.worst_settlement_entity ?? "—").slice(0, 16)} sub={`SDI ${data.executive?.worst_sdi ?? "—"}`} tone="red" />
          </div>
        </>
      )}
    </Shell>
  );
}
