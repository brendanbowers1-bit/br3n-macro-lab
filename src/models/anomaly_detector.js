/** Simple robust z-score anomaly detector. */
function percentile(values, p) {
  const s = [...values].filter(Number.isFinite).sort((a, b) => a - b);
  if (!s.length) return 0;
  return s[Math.floor((s.length - 1) * p)];
}

function anomalyDetector(row, history) {
  const fields = ["usd_return_1d", "spread_proxy_bps", "liquidity_proxy", "volatility_20d"];
  const triggered = [];
  let maxZ = 0;

  for (const f of fields) {
    const vals = history.map((r) => parseFloat(r[f])).filter(Number.isFinite);
    const x = parseFloat(row[f]);
    if (!vals.length || !Number.isFinite(x)) continue;
    const med = percentile(vals, 0.5);
    const mad = percentile(vals.map((v) => Math.abs(v - med)), 0.5) || 1e-6;
    const z = Math.abs(0.6745 * (x - med) / mad);
    if (z > 2.5) triggered.push({ field: f, robust_z: z.toFixed(2) });
    maxZ = Math.max(maxZ, z);
  }

  const score = Math.min(100, Math.round(maxZ * 15));

  return {
    anomaly_score: score,
    triggered_fields: triggered,
    explanation:
      triggered.length
        ? `Robust z-score exceeded threshold on: ${triggered.map((t) => t.field).join(", ")}.`
        : "No field exceeded robust z-score threshold on latest row.",
  };
}

module.exports = { anomalyDetector };
