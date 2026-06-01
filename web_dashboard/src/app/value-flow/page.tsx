"use client";

import { Shell } from "@/components/Shell";
import { Badge } from "@/components/ui/badge";
import { ValueFlowMap } from "@/components/charts/ValueFlowMap";
import { EChart } from "@/components/charts/EChart";
import { ChartPanel, CredibilityBanner, LoadingPulse } from "@/components/shared/Premium";
import { useDashboard } from "@/components/DashboardProvider";
import { vsiBarOption } from "@/lib/charts/options";

export default function ValueFlowPage() {
  const { data, loading } = useDashboard();
  const lines = data?.visualizations?.value_flow_lines ?? [];

  return (
    <Shell title="Global Value Flow Map" subtitle="3D-feeling corridor arcs · leakage-weighted paths" wide>
      <CredibilityBanner>
        Arc width scales with estimated loss per $100 sent. Coordinates from corridor sender/receiver countries in the Python export.
      </CredibilityBanner>

      {loading && !data && <LoadingPulse message="Loading value flow topology…" />}

      {data && (
        <>
          <ChartPanel
            title="Remittance corridor value flow"
            caption={`${lines.length} corridors with geo coordinates · drag to rotate · scroll to zoom`}
            badge={<Badge variant="default">GEO LINES</Badge>}
          >
            <ValueFlowMap lines={lines} height={560} />
          </ChartPanel>

          <ChartPanel title="Corridor VSI ranking" caption="Same corridors as flow map">
            <EChart
              option={vsiBarOption(
                lines.map((l) => l.corridor.slice(0, 22)),
                lines.map((l) => l.vsi)
              )}
              height={320}
            />
          </ChartPanel>
        </>
      )}
    </Shell>
  );
}
