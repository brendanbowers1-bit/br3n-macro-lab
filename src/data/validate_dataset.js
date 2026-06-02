/** Validate USD/MXN canonical dataset (Node). */
const fs = require("fs");
const path = require("path");
const rules = require("./validation_rules");

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/).filter(Boolean);
  const headers = lines[0].split(",");
  return lines.slice(1).map((line) => {
    const vals = line.split(",");
    const row = {};
    headers.forEach((h, i) => { row[h.trim()] = (vals[i] || "").trim(); });
    return row;
  });
}

function validateDataset(filePath) {
  const checks = [];
  let status = "Pass";

  if (!fs.existsSync(filePath)) {
    return { status: "Fail", checks: [{ id: "file_exists", status: "fail", message: "Dataset file missing" }] };
  }

  checks.push({ id: "file_exists", status: "pass" });
  const rows = parseCsv(fs.readFileSync(filePath, "utf8"));

  const missingCols = rules.required_columns.filter((c) => !(rows[0] && c in rows[0]));
  if (missingCols.length) {
    checks.push({ id: "required_columns", status: "fail", message: `Missing: ${missingCols.join(", ")}` });
    status = "Fail";
  } else {
    checks.push({ id: "required_columns", status: "pass" });
  }

  const dates = rows.map((r) => r.date);
  const parsedDates = dates.map((d) => new Date(d + "T12:00:00Z"));
  const invalidDates = parsedDates.filter((d) => Number.isNaN(d.getTime()));
  if (invalidDates.length) {
    checks.push({ id: "valid_dates", status: "fail", message: `${invalidDates.length} invalid dates` });
    status = "Fail";
  } else {
    checks.push({ id: "valid_dates", status: "pass" });
  }

  const dupes = dates.filter((d, i) => dates.indexOf(d) !== i);
  if (dupes.length) {
    checks.push({ id: "duplicate_dates", status: "fail", message: "Duplicate dates found" });
    status = "Fail";
  } else {
    checks.push({ id: "duplicate_dates", status: "pass" });
  }

  const sorted = [...dates].sort();
  if (JSON.stringify(dates) !== JSON.stringify(sorted)) {
    checks.push({ id: "monotonic_date_ordering", status: "fail" });
    status = "Fail";
  } else {
    checks.push({ id: "monotonic_date_ordering", status: "pass" });
  }

  const missingByCol = {};
  for (const col of ["usd_mxn_spot", "us_policy_rate", "mx_policy_rate"]) {
    missingByCol[col] = rows.filter((r) => r[col] === "" || r[col] == null).length;
  }
  checks.push({ id: "missing_values", status: "pass", message: missingByCol });

  let extreme = 0;
  for (const r of rows) {
    const ret = parseFloat(r.usd_return_1d);
    if (Number.isFinite(ret) && Math.abs(ret) > rules.max_daily_move_pct) extreme++;
  }
  if (extreme) {
    checks.push({ id: "suspicious_extreme_one_day_change", status: "warn", message: `${extreme} rows > 5%` });
    if (status === "Pass") status = "Warning";
  } else {
    checks.push({ id: "suspicious_extreme_one_day_change", status: "pass" });
  }

  const badRegime = rows.filter((r) => r.volatility_regime && !rules.valid_volatility_regimes.includes(r.volatility_regime));
  if (badRegime.length) {
    checks.push({ id: "volatility_regime", status: "fail", message: "Invalid regime values" });
    status = "Fail";
  } else {
    checks.push({ id: "volatility_regime", status: "pass" });
  }

  const dataMode = rows[0]?.data_mode || "";
  if (!rules.valid_data_modes.includes(dataMode)) {
    checks.push({ id: "data_mode", status: "fail", message: `Invalid data_mode: ${dataMode}` });
    status = "Fail";
  } else {
    checks.push({ id: "data_mode", status: "pass", message: dataMode });
    if (dataMode === "synthetic" || dataMode === "sample") {
      checks.push({ id: "synthetic_disclosure", status: "warn", message: "Dataset is synthetic/sample — not live market data" });
      if (status === "Pass") status = "Warning";
    }
  }

  if (!rows[0]?.source_lineage) {
    checks.push({ id: "source_lineage", status: "fail" });
    status = "Fail";
  } else {
    checks.push({ id: "source_lineage", status: "pass" });
  }

  const latest = dates[dates.length - 1];
  const ageDays = (Date.now() - new Date(latest + "T12:00:00Z").getTime()) / 86400000;
  if (ageDays > rules.stale_days_warning) {
    checks.push({ id: "stale_source_warning", status: "warn", message: `Latest date ${latest} is ${Math.floor(ageDays)} days old` });
    if (status === "Pass") status = "Warning";
  }

  for (const r of rows) {
    if (r.event_flag === "true" && !r.event_description) {
      checks.push({ id: "event_descriptions", status: "fail", message: `Missing event description on ${r.date}` });
      status = "Fail";
      break;
    }
    if (r.holiday_flag === "true" && !r.holiday_description) {
      checks.push({ id: "holiday_descriptions", status: "fail", message: `Missing holiday description on ${r.date}` });
      status = "Fail";
      break;
    }
  }
  if (!checks.find((c) => c.id === "event_descriptions")) checks.push({ id: "event_descriptions", status: "pass" });
  if (!checks.find((c) => c.id === "holiday_descriptions")) checks.push({ id: "holiday_descriptions", status: "pass" });

  return {
    status,
    rows: rows.length,
    date_min: dates[0],
    date_max: latest,
    data_mode: dataMode,
    checks,
    generated_at: new Date().toISOString(),
    dataset_path: filePath,
  };
}

module.exports = { validateDataset, parseCsv };
