#!/usr/bin/env node
/** End-to-end Bowers Frontier Macro Labs USD/MXN system pipeline. */
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const {
  CANONICAL_SAMPLE,
  VALIDATION_JSON,
  MODEL_JSON,
  BRIEF_MD,
  BRIEF_JSON,
  EVAL_JSON,
  VECTOR_STORE,
  SYSTEM_JSON,
  SYSTEM_MD,
  WEB_API,
} = require("./lib/paths");

function run(cmd, label) {
  try {
    execSync(cmd, { stdio: "inherit", cwd: path.join(__dirname, "..") });
    return { step: label, status: "pass" };
  } catch (e) {
    return { step: label, status: "fail", error: String(e.message || e) };
  }
}

function exists(p) {
  return fs.existsSync(p);
}

function exportModelLabApi(payload) {
  fs.mkdirSync(path.dirname(WEB_API), { recursive: true });
  fs.writeFileSync(WEB_API, JSON.stringify(payload, null, 2));
}

function main() {
  const steps = [];
  steps.push(run("node scripts/build_usd_mxn_sample_dataset.js", "dataset_build"));
  steps.push(run("node scripts/validate_usd_mxn_dataset.js", "validation"));
  steps.push(run("node scripts/run_usd_mxn_models.js", "model_run"));
  steps.push(run("node model-lab/scripts/ingest_documents.js", "rag_ingest"));
  steps.push(run("node model-lab/scripts/run_corridor_brief.js", "brief_generation"));
  steps.push(run("node model-lab/scripts/run_evals.js", "eval_suite"));

  const outputs = {
    canonical_dataset: exists(CANONICAL_SAMPLE),
    validation_report: exists(VALIDATION_JSON),
    model_run: exists(MODEL_JSON),
    brief_md: exists(BRIEF_MD),
    brief_json: exists(BRIEF_JSON),
    eval_report: exists(EVAL_JSON),
    vector_store: exists(VECTOR_STORE),
  };
  const dashboardOk = Object.values(outputs).every(Boolean);

  let validation = null;
  let model = null;
  let brief = null;
  if (exists(VALIDATION_JSON)) validation = JSON.parse(fs.readFileSync(VALIDATION_JSON, "utf8"));
  if (exists(MODEL_JSON)) model = JSON.parse(fs.readFileSync(MODEL_JSON, "utf8"));
  if (exists(BRIEF_JSON)) brief = JSON.parse(fs.readFileSync(BRIEF_JSON, "utf8"));

  const warnings = steps.filter((s) => s.status === "fail").map((s) => `${s.step} failed`);
  if (validation?.status === "Warning") warnings.push("Validation completed with warnings (expected for synthetic data)");
  if (brief?.llm_error) warnings.push(`LLM brief supplement unavailable: ${brief.llm_error}`);

  const report = {
    lab: "Bowers Frontier Macro Labs",
    generated_at: new Date().toISOString(),
    environment: { node: process.version, model_provider: process.env.MODEL_PROVIDER || "ollama" },
    data_mode: model?.data_mode || validation?.data_mode || "unknown",
    pipeline_results: steps,
    key_outputs: outputs,
    dashboard_output_check: dashboardOk ? "pass" : "fail",
    validation_status: validation?.status,
    corridor_risk_score: model?.corridor_risk_score?.score,
    corridor_risk_regime: model?.corridor_risk_score?.regime,
    warnings,
    next_required_work: [
      "Set BANXICO_SIE_TOKEN for official Banxico SIE series",
      "Replace synthetic sample with validated live lake outputs where appropriate",
      "Run model:smoke when Ollama/LM Studio available",
      "Expand eval live runs to full 25-question battery",
    ],
  };

  fs.mkdirSync(path.dirname(SYSTEM_JSON), { recursive: true });
  fs.writeFileSync(SYSTEM_JSON, JSON.stringify(report, null, 2));

  const md = `# Bowers Frontier Macro Labs — System Status

Generated at: ${report.generated_at}
Environment: Node ${process.version}
Data mode: ${report.data_mode}

## Pipeline Results
${steps.map((s) => `- ${s.step}: **${s.status}**${s.error ? ` (${s.error})` : ""}`).join("\n")}

## Key Outputs
${Object.entries(outputs).map(([k, v]) => `- ${k}: ${v ? "OK" : "MISSING"}`).join("\n")}

## Corridor Risk Score
${model ? `${model.corridor_risk_score.score}/100 (${model.corridor_risk_score.regime})` : "n/a"}

## Warnings
${warnings.length ? warnings.map((w) => `- ${w}`).join("\n") : "None"}

## Next Required Work
${report.next_required_work.map((w) => `- ${w}`).join("\n")}
`;
  fs.writeFileSync(SYSTEM_MD, md);

  exportModelLabApi({
    ...report,
    brief_path: BRIEF_MD,
    methodology_doc: "docs/methodology_usd_mxn_corridor_risk_framework.md",
    live_lake_note: "Python pipeline (npm run lake:run) provides mixed/live canonical parquet separately from synthetic sample CSV.",
  });

  if (exists(BRIEF_MD)) {
    const preview = fs.readFileSync(BRIEF_MD, "utf8").slice(0, 8000);
    fs.writeFileSync(path.join(path.dirname(WEB_API), "brief_preview.txt"), preview);
  }

  console.log("\nrun_bowers_frontier_pipeline", dashboardOk ? "PASS" : "PARTIAL");
  if (!dashboardOk) process.exit(1);
}

main();
