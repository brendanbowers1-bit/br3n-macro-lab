"use client";

import { motion } from "framer-motion";
import { Shell } from "@/components/Shell";
import { Badge } from "@/components/ui/badge";
import { EChart } from "@/components/charts/EChart";
import { AnimatedKpi, ChartPanel, CredibilityBanner, CinematicHero, LoadingPulse } from "@/components/shared/Premium";
import { useDashboard } from "@/components/DashboardProvider";
import { vsiBarOption } from "@/lib/charts/options";

export default function CommandCenterPage() {
  const { data, loading } = useDashboard();
  const exec = data?.executive ?? {};
  const corridors = data?.vsi?.corridor_summary ?? [];
  const sorted = [...corridors].sort(
    (a, b) => Number(a.value_survival_index ?? 0) - Number(b.value_survival_index ?? 0)
  );
  const worst = sorted.slice(0, 10);

  return (
    <Shell title="Executive Command Center" subtitle="Cross-lab KPIs · animated risk overview" wide>
      <CredibilityBanner>
        Research and education only. Not investment advice. Verify mock_data_flag before citing outputs.
        Data exported from Python pipeline at {data?.meta?.generated_at?.slice(0, 19) ?? "—"} UTC.
      </CredibilityBanner>

      {loading && !data && <LoadingPulse />}

      {data && (
        <>
          <CinematicHero>
            <div className="flex flex-wrap items-center gap-2 mb-4">
              <Badge variant="default">LIVE EXPORT</Badge>
              <Badge variant="muted">{Object.values(data.modules).filter(Boolean).length}/5 modules</Badge>
            </div>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm text-textSecondary max-w-2xl"
            >
              Command center synthesizes VSI corridors, settlement drag, stablecoin finality, and data lake health
              from exported JSON — no client-side computation.
            </motion.p>
          </CinematicHero>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <AnimatedKpi label="Global VSI" value={exec.global_vsi != null ? Number(exec.global_vsi).toFixed(1) : "—"} sub="Mean corridor" tone="cyan" delay={0} />
            <AnimatedKpi label="Worst corridor" value={String(exec.worst_corridor ?? "—").slice(0, 22)} sub={`VSI ${exec.worst_vsi ?? "—"}`} tone="red" delay={0.05} />
            <AnimatedKpi label="Loss / $100" value={exec.avg_loss_per_100 != null ? `$${Number(exec.avg_loss_per_100).toFixed(2)}` : "—"} tone="amber" delay={0.1} />
            <AnimatedKpi label="Official coverage" value={exec.official_coverage_pct != null ? `${exec.official_coverage_pct}%` : "—"} tone="gold" delay={0.15} />
          </div>

          <div className="grid lg:grid-cols-3 gap-4">
            <ChartPanel title="Worst corridors (VSI)" caption="Lower = more value leakage" className="lg:col-span-2">
              <EChart option={vsiBarOption(
                worst.map((r) => String(r.corridor ?? "").slice(0, 20)),
                worst.map((r) => Number(r.value_survival_index ?? 0))
              )} height={340} />
            </ChartPanel>
            <ChartPanel title="Module status" caption="Pipeline connectivity">
              <div className="grid grid-cols-1 gap-2 mt-1">
                {Object.entries(data.modules).map(([k, v]) => (
                  <div
                    key={k}
                    className={`flex items-center justify-between text-xs px-3 py-2.5 rounded-lg border ${
                      v ? "border-successGreen/35 bg-successGreen/5 text-successGreen" : "border-warningAmber/35 bg-warningAmber/5 text-warningAmber"
                    }`}
                  >
                    <span className="uppercase tracking-wider">{k.replace("_", " ")}</span>
                    <span className="font-mono">{v ? "ONLINE" : "OFF"}</span>
                  </div>
                ))}
              </div>
            </ChartPanel>
          </div>

          <div className="grid md:grid-cols-3 gap-3">
            <AnimatedKpi label="Worst SDI entity" value={String(exec.worst_settlement_entity ?? "—").slice(0, 20)} sub={`SDI ${exec.worst_sdi ?? "—"}`} tone="purple" />
            <AnimatedKpi label="Worst stablecoin" value={String(exec.worst_stablecoin ?? "—")} sub={`SFQI ${exec.worst_sfqi ?? "—"}`} tone="cyan" />
            <AnimatedKpi label="Hypotheses loaded" value={String((data.hypotheses?.vsi?.length ?? 0) + (data.hypotheses?.settlement?.length ?? 0) + (data.hypotheses?.stablecoin?.length ?? 0))} sub="Across labs" tone="green" />
          </div>
        </>
      )}
    </Shell>
  );
}
