"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { Badge } from "@/components/ui/badge";
import { AnimatedKpi, ChartPanel, CredibilityBanner, LoadingPulse } from "@/components/shared/Premium";
import { withBasePath } from "@/lib/base-path";

type ModelLabPayload = {
  data_mode?: string;
  validation_status?: string;
  corridor_risk_score?: number;
  corridor_risk_regime?: string;
  pipeline_results?: { step: string; status: string }[];
  key_outputs?: Record<string, boolean>;
  warnings?: string[];
  generated_at?: string;
  environment?: { model_provider?: string };
  live_lake_note?: string;
};

export default function ModelLabPage() {
  const [data, setData] = useState<ModelLabPayload | null>(null);
  const [briefPreview, setBriefPreview] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(withBasePath("/api/model_lab.json"));
        if (res.ok) setData(await res.json());
      } catch {
        /* optional file */
      }
      setLoading(false);
    }
    load();
  }, []);

  useEffect(() => {
    fetch(withBasePath("/api/brief_preview.txt"))
      .then((r) => (r.ok ? r.text() : ""))
      .then(setBriefPreview)
      .catch(() => undefined);
  }, []);

  const crs = data?.corridor_risk_score;
  const isSynthetic = data?.data_mode === "synthetic";

  return (
    <Shell
      title="Bowers Frontier Model Lab"
      subtitle="Model-agnostic AI research environment for FX, treasury, settlement, and corridor-risk tasks"
      wide
    >
      <CredibilityBanner>
        Research and decision support only — not financial advice.{" "}
        {isSynthetic ? (
          <strong className="text-warningAmber">Sample/synthetic data mode active.</strong>
        ) : (
          "Review data_mode and validation status before citing outputs."
        )}
      </CredibilityBanner>

      {loading && <LoadingPulse />}

      {data && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <AnimatedKpi label="Data mode" value={String(data.data_mode ?? "—")} tone={isSynthetic ? "amber" : "green"} />
            <AnimatedKpi label="Validation" value={String(data.validation_status ?? "—")} tone="cyan" />
            <AnimatedKpi
              label="Corridor risk"
              value={crs != null ? `${crs}/100` : "—"}
              sub={data.corridor_risk_regime}
              tone="gold"
            />
            <AnimatedKpi label="Provider" value={data.environment?.model_provider ?? "ollama"} tone="purple" />
          </div>

          <ChartPanel title="System status" badge={<Badge variant="default">system:run</Badge>}>
            <div className="grid md:grid-cols-2 gap-4 text-xs font-mono">
              <div>
                <p className="text-textPrimary mb-2 uppercase tracking-wider">Pipeline</p>
                {(data.pipeline_results ?? []).map((s) => (
                  <p key={s.step} className={s.status === "pass" ? "text-successGreen" : "text-riskRed"}>
                    {s.step}: {s.status}
                  </p>
                ))}
              </div>
              <div>
                <p className="text-textPrimary mb-2 uppercase tracking-wider">Outputs</p>
                {Object.entries(data.key_outputs ?? {}).map(([k, v]) => (
                  <p key={k}>
                    {k}: {v ? "OK" : "missing"}
                  </p>
                ))}
              </div>
            </div>
            {data.warnings?.length ? (
              <div className="mt-4 text-xs text-warningAmber">
                {data.warnings.map((w) => (
                  <p key={w}>⚠ {w}</p>
                ))}
              </div>
            ) : null}
            {data.live_lake_note ? <p className="mt-3 text-xs text-textSecondary">{data.live_lake_note}</p> : null}
          </ChartPanel>

          <ChartPanel title="USD/MXN corridor intelligence" caption="Transparent model layer — not a trading signal">
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 text-sm">
              <div className="rounded-lg border border-border/60 p-3">
                <p className="text-xs text-textSecondary">Risk score</p>
                <p className="text-xl font-semibold text-accentGold">{crs ?? "—"}/100</p>
              </div>
              <div className="rounded-lg border border-border/60 p-3">
                <p className="text-xs text-textSecondary">Regime</p>
                <p className="text-lg">{data.corridor_risk_regime ?? "—"}</p>
              </div>
              <div className="rounded-lg border border-border/60 p-3">
                <p className="text-xs text-textSecondary">Validation</p>
                <p className="text-lg">{data.validation_status ?? "—"}</p>
              </div>
              <div className="rounded-lg border border-border/60 p-3">
                <p className="text-xs text-textSecondary">Generated</p>
                <p className="text-xs font-mono">{data.generated_at?.slice(0, 19) ?? "—"}</p>
              </div>
            </div>
          </ChartPanel>

          <ChartPanel title="Architecture" caption="End-to-end research pipeline">
            <pre className="text-[0.65rem] text-textSecondary overflow-x-auto whitespace-pre-wrap font-mono leading-relaxed">
              {`Data Sources → Raw Data Lake → Validation → Feature Store → Transparent Models → RAG → LLM Provider → Brief Generator → Dashboard → Evals`}
            </pre>
          </ChartPanel>

          {briefPreview ? (
            <ChartPanel title="Latest corridor brief (preview)" badge={<Badge variant="muted">deterministic + optional LLM</Badge>}>
              <pre className="text-xs text-textSecondary whitespace-pre-wrap max-h-96 overflow-y-auto font-mono">{briefPreview.slice(0, 3500)}</pre>
            </ChartPanel>
          ) : (
            <ChartPanel title="Latest corridor brief">
              <p className="text-sm text-textSecondary">Run <code>npm run system:run</code> to generate outputs/briefs/usd_mxn_latest.md</p>
            </ChartPanel>
          )}
        </>
      )}

      {!loading && !data && (
        <ChartPanel title="Model Lab not initialized">
          <p className="text-sm text-textSecondary">
            Run <code className="text-accentCyan">npm run system:run</code> from the repo root, then rebuild or refresh.
          </p>
        </ChartPanel>
      )}
    </Shell>
  );
}
