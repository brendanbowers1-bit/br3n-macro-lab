"use client";

import { Shell } from "@/components/Shell";
import { Badge } from "@/components/ui/badge";
import { AnimatedKpi, ChartPanel, CredibilityBanner, LoadingPulse } from "@/components/shared/Premium";
import { useDashboard } from "@/components/DashboardProvider";

export default function AuditPage() {
  const { data, loading } = useDashboard();
  const audit = data?.audit ?? {};
  const qs = (audit.quality_summary ?? {}) as Record<string, number>;

  return (
    <Shell title="Data Quality & Audit" subtitle="Validation · tests · credibility tracking">
      <CredibilityBanner>
        Mixed-mode data in settlement/stablecoin modules. Check mock_data_flag per table before publication or citation.
      </CredibilityBanner>

      {loading && !data && <LoadingPulse />}

      {data && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <AnimatedKpi label="Quality PASS" value={String(qs.pass ?? "—")} tone="green" />
            <AnimatedKpi label="Quality FAIL" value={String(qs.fail ?? "—")} tone="red" />
            <AnimatedKpi
              label="Snapshot"
              value={String(audit.latest_snapshot ?? "none").split("/").pop()?.slice(0, 18) ?? "—"}
              tone="gold"
            />
            <AnimatedKpi
              label="Hypotheses"
              value={String(
                (data.hypotheses?.vsi?.length ?? 0) +
                  (data.hypotheses?.settlement?.length ?? 0) +
                  (data.hypotheses?.stablecoin?.length ?? 0)
              )}
              sub="Across labs"
              tone="cyan"
            />
          </div>

          <ChartPanel title="Module coverage (mock %)" caption="Lower mock % = higher official data share" badge={<Badge variant="amber">AUDIT</Badge>}>
            <div className="grid md:grid-cols-3 gap-4">
              {Object.entries(data.coverage ?? {}).map(([mod, tables]) => (
                <div key={mod} className="rounded-lg border border-border/50 p-3 bg-surfaceAlt/30">
                  <div className="text-xs uppercase tracking-wider text-accentCyan mb-2">{mod}</div>
                  <ul className="space-y-1 text-xs text-textSecondary font-mono">
                    {Object.entries(tables as Record<string, number | null>).map(([t, pct]) => (
                      <li key={t} className="flex justify-between">
                        <span>{t}</span>
                        <span className={pct && pct > 50 ? "text-warningAmber" : "text-successGreen"}>
                          {pct ?? 0}% mock
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </ChartPanel>

          <ChartPanel title="Research hypotheses (sample)" caption="First entries from each lab">
            <div className="grid md:grid-cols-3 gap-4 text-xs text-textSecondary">
              {(["vsi", "settlement", "stablecoin"] as const).map((lab) => (
                <div key={lab}>
                  <div className="uppercase tracking-wider text-textPrimary mb-2">{lab}</div>
                  <ul className="space-y-2">
                    {(data.hypotheses?.[lab] ?? []).slice(0, 4).map((h, i) => (
                      <li key={i} className="border-l-2 border-border pl-2">
                        {String((h as Record<string, unknown>).hypothesis ?? (h as Record<string, unknown>).title ?? JSON.stringify(h).slice(0, 80))}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </ChartPanel>
        </>
      )}
    </Shell>
  );
}
