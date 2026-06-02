/** Shared paths for Bowers Frontier Macro Labs Node pipelines. */
const path = require("path");

const ROOT = path.resolve(__dirname, "../..");

module.exports = {
  ROOT,
  DATA_LAKE: path.join(ROOT, "data-lake"),
  RAW_FX: path.join(ROOT, "data-lake/raw/fx"),
  RAW_RATES: path.join(ROOT, "data-lake/raw/rates"),
  RAW_EVENTS: path.join(ROOT, "data-lake/raw/events"),
  RAW_HOLIDAYS: path.join(ROOT, "data-lake/raw/holidays"),
  RAW_REMIT: path.join(ROOT, "data-lake/raw/remittances"),
  PROCESSED: path.join(ROOT, "data-lake/processed/corridors"),
  VALIDATION_REPORTS: path.join(ROOT, "data-lake/metadata/validation_reports"),
  OUTPUTS: path.join(ROOT, "outputs"),
  MODEL_RUNS: path.join(ROOT, "outputs/model-runs"),
  BRIEFS: path.join(ROOT, "outputs/briefs"),
  EVALS: path.join(ROOT, "outputs/evals"),
  MODEL_LAB: path.join(ROOT, "model-lab"),
  VECTOR_STORE: path.join(ROOT, "model-lab/outputs/vector_store.json"),
  WEB_API: path.join(ROOT, "web_dashboard/public/api/model_lab.json"),
  SAMPLE_RAW: {
    fx: path.join(ROOT, "data-lake/raw/fx/usd_mxn_spot_sample.csv"),
    fed: path.join(ROOT, "data-lake/raw/rates/fed_policy_rate_sample.csv"),
    banxico: path.join(ROOT, "data-lake/raw/rates/banxico_policy_rate_sample.csv"),
    events: path.join(ROOT, "data-lake/raw/events/usd_mxn_macro_events_sample.json"),
    holidays: path.join(ROOT, "data-lake/raw/holidays/us_mx_holidays_sample.json"),
    remit: path.join(ROOT, "data-lake/raw/remittances/us_mx_remittance_cost_sample.csv"),
  },
  CANONICAL_SAMPLE: path.join(ROOT, "data-lake/processed/corridors/usd_mxn_canonical_sample.csv"),
  VALIDATION_JSON: path.join(ROOT, "data-lake/metadata/validation_reports/usd_mxn_validation_latest.json"),
  VALIDATION_MD: path.join(ROOT, "data-lake/metadata/validation_reports/usd_mxn_validation_latest.md"),
  MODEL_JSON: path.join(ROOT, "outputs/model-runs/usd_mxn_model_latest.json"),
  MODEL_MD: path.join(ROOT, "outputs/model-runs/usd_mxn_model_latest.md"),
  BRIEF_MD: path.join(ROOT, "outputs/briefs/usd_mxn_latest.md"),
  BRIEF_JSON: path.join(ROOT, "outputs/briefs/usd_mxn_latest.json"),
  EVAL_JSON: path.join(ROOT, "outputs/evals/eval_results_latest.json"),
  EVAL_MD: path.join(ROOT, "outputs/evals/eval_report_latest.md"),
  SYSTEM_JSON: path.join(ROOT, "outputs/system_status_latest.json"),
  SYSTEM_MD: path.join(ROOT, "outputs/system_status_latest.md"),
};
