"use client";

import { Shell } from "@/components/Shell";
import { Badge } from "@/components/ui/badge";
import { EChart } from "@/components/charts/EChart";
import { ChartPanel, CredibilityBanner, LoadingPulse } from "@/components/shared/Premium";
import { useDashboard } from "@/components/DashboardProvider";
import { finalityMatrixOption, sankeyOption } from "@/lib/charts/options";

export default function StablecoinsPage() {
  const { data, loading } = useDashboard();
  const matrix = data?.visualizations?.finality_matrix ?? [];
  const riskSankey = data?.visualizations?.risk_relocation_sankey;
  const sfqi = data?.stablecoin?.finality_quality ?? [];

  const scatterRows = matrix.length
    ? matrix.map((r) => ({
        stablecoin: String(r.stablecoin),
        ledger: Number(r.ledger_finality_score ?? 0),
        economic: Number(r.economic_finality_score ?? 0),
        sfqi: Number(r.stablecoin_finality_quality_index ?? 0),
      }))
    : sfqi.map((r) => ({
        stablecoin: String(r.stablecoin),
        ledger: Number(r.ledger_finality_score ?? 0),
        economic: Number(r.economic_finality_score ?? 0),
        sfqi: Number(r.stablecoin_finality_quality_index ?? 0),
      }));

  return (
    <Shell title="Stablecoin Settlement Windows" subtitle="Finality matrix · risk relocation Sankey" wide>
      <CredibilityBanner>
        Ledger vs economic finality gap highlights settlement window risk. Risk relocation Sankey is conceptual under SWC spec — not causal.
        Check mock_data_flag on stablecoin tables before citing.
      </CredibilityBanner>

      {loading && !data && <LoadingPulse />}

      {data && (
        <>
          <div className="grid lg:grid-cols-2 gap-4">
            <ChartPanel
              title="Stablecoin finality matrix"
              caption="Bubble size = SFQI · color = ledger/economic gap"
              badge={<Badge variant="default">MATRIX</Badge>}
            >
              <EChart option={finalityMatrixOption(scatterRows)} height={420} />
            </ChartPanel>

            {riskSankey && (
              <ChartPanel
                title="Risk relocation (conceptual)"
                caption={riskSankey.note ?? "Counterparty risk shifts under stablecoin wrapper"}
                badge={<Badge variant="amber">SANKEY</Badge>}
              >
                <EChart option={sankeyOption(riskSankey)} height={420} />
              </ChartPanel>
            )}
          </div>

          <ChartPanel title="SFQI detail" caption="From Python stablecoin lab export">
            <div className="overflow-auto max-h-80 rounded-lg border border-border/50">
              <table className="w-full text-xs">
                <thead className="text-textSecondary border-b border-border bg-surfaceAlt/40">
                  <tr>
                    <th className="text-left p-2.5">Stablecoin</th>
                    <th className="text-right p-2.5">Ledger</th>
                    <th className="text-right p-2.5">Economic</th>
                    <th className="text-right p-2.5">SFQI</th>
                  </tr>
                </thead>
                <tbody>
                  {scatterRows.map((r, i) => (
                    <tr key={i} className="border-b border-border/40">
                      <td className="p-2.5">{r.stablecoin}</td>
                      <td className="p-2.5 text-right font-mono">{r.ledger.toFixed(1)}</td>
                      <td className="p-2.5 text-right font-mono">{r.economic.toFixed(1)}</td>
                      <td className="p-2.5 text-right font-mono">{r.sfqi.toFixed(1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ChartPanel>

          {data.hypotheses?.flagship_questions?.length > 0 && (
            <ChartPanel title="Flagship research questions" caption="Stablecoin lab hypotheses">
              <ul className="space-y-2 text-sm text-textSecondary">
                {data.hypotheses.flagship_questions.map((q, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-accentGold font-mono shrink-0">{String(i + 1).padStart(2, "0")}</span>
                    {q}
                  </li>
                ))}
              </ul>
            </ChartPanel>
          )}
        </>
      )}
    </Shell>
  );
}
