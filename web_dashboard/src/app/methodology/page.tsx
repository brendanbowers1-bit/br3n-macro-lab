"use client";

import { Shell } from "@/components/Shell";
import { Badge } from "@/components/ui/badge";
import { ChartPanel, CredibilityBanner } from "@/components/shared/Premium";

const SECTIONS = [
  {
    title: "Purpose",
    body: "This framework studies USD/MXN corridor risk across FX, rates, volatility, settlement, liquidity, remittance, and macro-event dimensions — as an explainable research indicator.",
  },
  {
    title: "What the score is",
    body: "The corridor risk score is a transparent 0–100 research indicator built from volatility, spread/liquidity proxies, rate differential movement, event and holiday flags, and anomaly detection.",
  },
  {
    title: "What the score is not",
    body: "Not a trading signal, forecast, guarantee, financial advice, or substitute for market judgment.",
  },
  {
    title: "Data inputs",
    body: "USD/MXN spot, US and Mexico policy rates, rate differential, volatility, spread and liquidity proxies, event/holiday flags, remittance cost proxy — each with source lineage in data-lake/metadata/.",
  },
  {
    title: "Data quality standards",
    body: "Source registry, immutable raw layer, validation reports, explicit data_mode (synthetic/sample/live/mixed), stale-data warnings.",
  },
  {
    title: "Model layer",
    body: "Transparent JavaScript/Python models run before LLM narrative. LLMs explain structured outputs; they do not create market facts. RAG adds research context only.",
  },
  {
    title: "Evaluation",
    body: "25-question eval battery scores factuality, domain specificity, data grounding, uncertainty handling, hallucination control, and financial safety.",
  },
  {
    title: "Limitations",
    body: "Sample data is synthetic until live connectors succeed. Proxies are imperfect. Remittance and liquidity series may be quarterly or research-grade only.",
  },
];

export default function MethodologyPage() {
  return (
    <Shell title="Methodology: USD/MXN Corridor Risk Framework" subtitle="Transparent scoring for research and treasury decision support" wide>
      <CredibilityBanner>
        Full document: <code className="text-accentCyan">docs/methodology_usd_mxn_corridor_risk_framework.md</code> · Research only · Not financial advice
      </CredibilityBanner>

      <div className="space-y-4">
        {SECTIONS.map((s) => (
          <ChartPanel key={s.title} title={s.title} badge={<Badge variant="muted">FRAMEWORK</Badge>}>
            <p className="text-sm text-textSecondary leading-relaxed">{s.body}</p>
          </ChartPanel>
        ))}
      </div>
    </Shell>
  );
}
