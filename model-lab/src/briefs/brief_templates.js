const BRIEF_DISCLAIMER =
  "Research and decision support only. Not investment advice. Not a trading signal.";

function executiveBullets(model, validation) {
  const crs = model.corridor_risk_score;
  return [
    `Corridor risk score ${crs.score}/100 (${crs.regime}) on ${model.as_of} — ${model.data_mode} data.`,
    `Volatility regime: ${model.volatility_regime.regime}; carry signal: ${model.carry_signal.signal}.`,
    `Validation status: ${validation?.status || model.validation_status}.`,
    `Anomaly score ${model.anomaly_detector.anomaly_score}/100 — ${model.anomaly_detector.explanation}`,
    model.data_mode === "synthetic"
      ? "Dataset uses clearly labeled synthetic/sample data — not live market feeds."
      : "Review data_mode and source lineage before operational use.",
  ];
}

function deterministicBrief({ model, validation, rag }) {
  const crs = model.corridor_risk_score;
  const snap = model.latest_snapshot;
  return `# Bowers Frontier Macro Labs — USD/MXN Corridor Intelligence Brief

Corridor: USD/MXN (United States → Mexico)
Date: ${model.as_of}
Data Mode: **${model.data_mode}**
Model Provider: deterministic_fallback
Model Name: transparent_models_v1
Validation Status: ${validation?.status || model.validation_status}

## Executive Summary
${executiveBullets(model, validation).map((b) => `- ${b}`).join("\n")}

## Market Snapshot
- Spot: ${snap.usd_mxn_spot}
- Volatility regime: ${snap.volatility_regime}
- Rate differential: ${snap.rate_differential}%
- Carry proxy aligns with rate differential (research only)

## Corridor Risk Score
Score: **${crs.score}/100**
Regime: **${crs.regime}**

Component breakdown:
${Object.entries(crs.component_breakdown).map(([k, v]) => `- ${k}: ${v}`).join("\n")}

## What Changed
Latest row reflects ${snap.event_flag === "true" ? "an active macro event flag" : "no macro event flag"} and ${snap.holiday_flag === "true" ? "a holiday/settlement flag" : "no holiday flag"}.

## Treasury / Settlement Watchpoints
Monitor cut-off calendars, holiday liquidity, and remittance cost proxies. This brief does not provide operational payment instructions.

## Stablecoin / Alternative Settlement Notes
On-chain rails may alter settlement windows but introduce separate issuer and off-ramp risks. Non-hype research context only.

## Model Confidence
${model.data_mode === "synthetic" ? "Low–Medium (synthetic sample data)" : "Medium (subject to validation)"}

## Data Limitations
${crs.limitations}
${model.data_mode === "synthetic" ? "This run uses synthetic/sample data explicitly labeled in the canonical dataset." : ""}

## RAG Context Used
${rag?.chunks?.length ? rag.chunks.map((c) => `- ${c.source} (score ${c.score})`).join("\n") : "No RAG chunks retrieved (baseline keyword store)."}

## Not Financial Advice
${BRIEF_DISCLAIMER}
`;
}

module.exports = { deterministicBrief, BRIEF_DISCLAIMER, executiveBullets };
