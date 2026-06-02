#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const { parseCsv } = require("../src/data/validate_dataset");
const { carrySignal } = require("../src/models/carry_signal");
const { volatilityRegime } = require("../src/models/volatility_regime");
const { anomalyDetector } = require("../src/models/anomaly_detector");
const { corridorRiskScore } = require("../src/models/corridor_risk_score");
const { CANONICAL_SAMPLE, MODEL_JSON, MODEL_MD, VALIDATION_JSON } = require("./lib/paths");

function main() {
  if (!fs.existsSync(CANONICAL_SAMPLE)) {
    console.error("Missing canonical sample — run npm run data:build:usd-mxn first");
    process.exit(1);
  }
  const rows = parseCsv(fs.readFileSync(CANONICAL_SAMPLE, "utf8"));
  const latest = rows[rows.length - 1];
  const prev = rows[rows.length - 2];
  const history = rows.slice(-60);

  const spotTrend = parseFloat(latest.usd_return_5d) || 0;
  const carry = carrySignal({
    rateDifferential: parseFloat(latest.rate_differential),
    spotTrend,
    volatilityRegime: latest.volatility_regime,
  });
  const vol = volatilityRegime(parseFloat(latest.volatility_20d));
  const anomaly = anomalyDetector(latest, history);
  const crs = corridorRiskScore(latest, prev, anomaly);

  let validationStatus = "unknown";
  if (fs.existsSync(VALIDATION_JSON)) {
    validationStatus = JSON.parse(fs.readFileSync(VALIDATION_JSON, "utf8")).status;
  }

  const payload = {
    lab: "Bowers Frontier Macro Labs",
    corridor: "USD/MXN",
    as_of: latest.date,
    data_mode: latest.data_mode,
    dataset: CANONICAL_SAMPLE,
    validation_status: validationStatus,
    carry_signal: carry,
    volatility_regime: vol,
    anomaly_detector: anomaly,
    corridor_risk_score: crs,
    latest_snapshot: {
      usd_mxn_spot: latest.usd_mxn_spot,
      rate_differential: latest.rate_differential,
      volatility_regime: latest.volatility_regime,
      event_flag: latest.event_flag,
      holiday_flag: latest.holiday_flag,
    },
    generated_at: new Date().toISOString(),
    disclaimer: "Research and decision support only. Not investment advice. Not a trading signal.",
  };

  fs.mkdirSync(path.dirname(MODEL_JSON), { recursive: true });
  fs.writeFileSync(MODEL_JSON, JSON.stringify(payload, null, 2));

  const md = `# Bowers Frontier Macro Labs — USD/MXN Model Run

Date: ${latest.date}
Data mode: ${latest.data_mode}
Dataset: ${CANONICAL_SAMPLE}
Validation status: ${validationStatus}

## Carry Signal
- Signal: ${carry.signal}
- Confidence: ${carry.confidence}
- ${carry.explanation}

## Volatility Regime
- Regime: ${vol.regime}
- ${vol.explanation}

## Anomaly Detector
- Score: ${anomaly.anomaly_score}/100
- ${anomaly.explanation}

## Corridor Risk Score
- Score: ${crs.score}/100
- Regime: ${crs.regime}

### Component breakdown
${Object.entries(crs.component_breakdown).map(([k, v]) => `- ${k}: ${v}`).join("\n")}

## Limitations
${crs.limitations}

## Not Financial Advice
This is research and decision support, not a trading recommendation.
`;
  fs.writeFileSync(MODEL_MD, md);
  console.log("run_usd_mxn_models PASS");
  console.log(JSON.stringify({ score: crs.score, regime: crs.regime, carry: carry.signal }, null, 2));
}

main();
