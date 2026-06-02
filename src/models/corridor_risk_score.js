/** Transparent USD/MXN corridor risk score 0–100 (research, not prediction). */
const WEIGHTS = {
  volatility: 0.22,
  spread_liquidity: 0.18,
  rate_diff_change: 0.15,
  event_risk: 0.15,
  settlement_holiday: 0.12,
  anomaly: 0.18,
};

function clamp(x, lo = 0, hi = 100) {
  return Math.max(lo, Math.min(hi, x));
}

function band(score) {
  if (score < 25) return "Low";
  if (score < 50) return "Moderate";
  if (score < 75) return "Elevated";
  return "Severe";
}

function corridorRiskScore(latest, prev, anomaly) {
  const vol = parseFloat(latest.volatility_20d) || 0;
  const spread = parseFloat(latest.spread_proxy_bps) || 0;
  const liq = parseFloat(latest.liquidity_proxy);
  const diff = parseFloat(latest.rate_differential) || 0;
  const prevDiff = prev ? parseFloat(prev.rate_differential) || diff : diff;
  const diffChange = Math.abs(diff - prevDiff);

  const volComp = clamp(vol * 200);
  const spreadLiqComp = clamp(spread / 3 + (Number.isFinite(liq) ? (1 - liq) * 40 : 20));
  const rateChangeComp = clamp(diffChange * 25);
  const eventComp = latest.event_flag === "true" ? 70 : 15;
  const settleComp = latest.holiday_flag === "true" ? 55 : 10;
  const anomalyComp = anomaly?.anomaly_score ?? 0;

  const components = {
    volatility: +volComp.toFixed(2),
    spread_liquidity: +spreadLiqComp.toFixed(2),
    rate_diff_change: +rateChangeComp.toFixed(2),
    event_risk: +eventComp.toFixed(2),
    settlement_holiday: +settleComp.toFixed(2),
    anomaly: +anomalyComp.toFixed(2),
  };

  const score = clamp(
    components.volatility * WEIGHTS.volatility +
      components.spread_liquidity * WEIGHTS.spread_liquidity +
      components.rate_diff_change * WEIGHTS.rate_diff_change +
      components.event_risk * WEIGHTS.event_risk +
      components.settlement_holiday * WEIGHTS.settlement_holiday +
      components.anomaly * WEIGHTS.anomaly
  );

  return {
    score: +score.toFixed(1),
    regime: band(score),
    component_breakdown: components,
    weights: WEIGHTS,
    explanation:
      "Explainable research score from volatility, spread/liquidity proxies, rate differential change, macro events, settlement/holiday flags, and anomaly detector. Not a FX forecast.",
    limitations:
      "Uses synthetic/sample proxies where live connectors are unavailable. Spread and liquidity are research proxies, not executable market depth.",
    not_financial_advice: true,
  };
}

module.exports = { corridorRiskScore, WEIGHTS };
