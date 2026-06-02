/** Transparent carry signal (research only, not trading advice). */
function carrySignal({ rateDifferential, spotTrend, volatilityRegime }) {
  const diff = rateDifferential ?? 0;
  const trend = spotTrend ?? 0;
  let signal = "neutral";
  let confidence = 0.5;

  if (volatilityRegime === "crisis" || volatilityRegime === "elevated") {
    signal = "unstable";
    confidence = 0.7;
  } else if (diff > 3 && trend <= 0) {
    signal = "positive";
    confidence = 0.65;
  } else if (diff < 0) {
    signal = "negative";
    confidence = 0.6;
  }

  return {
    signal,
    confidence,
    explanation:
      `Rate differential ${diff.toFixed(2)}% with recent spot trend ${(trend * 100).toFixed(2)}% under ${volatilityRegime} vol regime. Research indicator only.`,
    not_financial_advice: true,
  };
}

module.exports = { carrySignal };
