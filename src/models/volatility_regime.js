/** Volatility regime classifier from 20d vol. */
const THRESHOLDS = { low: 0.08, normal: 0.14, elevated: 0.22 };

function volatilityRegime(vol20d) {
  const v = vol20d ?? 0;
  let regime = "normal";
  if (v <= THRESHOLDS.low) regime = "low";
  else if (v <= THRESHOLDS.normal) regime = "normal";
  else if (v <= THRESHOLDS.elevated) regime = "elevated";
  else regime = "crisis";

  return {
    regime,
    threshold_used: THRESHOLDS,
    input_volatility_20d: v,
    explanation: `20-day annualized vol ${v.toFixed(4)} mapped to ${regime} using fixed research thresholds.`,
  };
}

module.exports = { volatilityRegime, THRESHOLDS };
