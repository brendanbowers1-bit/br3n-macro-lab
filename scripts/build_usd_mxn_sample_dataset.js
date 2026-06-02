#!/usr/bin/env node
/** Build canonical USD/MXN sample dataset from labeled synthetic raw files. */
const fs = require("fs");
const { readCsv, writeCsv } = require("./lib/csv_utils");
const { ensureSampleRawFiles } = require("./lib/sample_raw_generator");
const { CANONICAL_SAMPLE, SAMPLE_RAW } = require("./lib/paths");

function num(v) {
  const n = parseFloat(v);
  return Number.isFinite(n) ? n : null;
}

function ffillQuarterly(dates, quarterly) {
  quarterly.sort((a, b) => a.date.localeCompare(b.date));
  let idx = 0;
  let cur = quarterly[0] || {};
  return dates.map((date) => {
    while (idx + 1 < quarterly.length && quarterly[idx + 1].date <= date) {
      idx++;
      cur = quarterly[idx];
    }
    return cur;
  });
}

function volRegime(vol, allVols) {
  const valid = allVols.filter((v) => v != null && !Number.isNaN(v));
  if (!valid.length || vol == null) return "unknown";
  const sorted = [...valid].sort((a, b) => a - b);
  const p33 = sorted[Math.floor(sorted.length * 0.33)] ?? 0;
  const p66 = sorted[Math.floor(sorted.length * 0.66)] ?? 0;
  const p90 = sorted[Math.floor(sorted.length * 0.9)] ?? 0;
  if (vol >= p90) return "crisis";
  if (vol >= p66) return "elevated";
  if (vol <= p33) return "low";
  return "normal";
}

function main() {
  const meta = ensureSampleRawFiles();
  const fx = readCsv(SAMPLE_RAW.fx);
  const fed = readCsv(SAMPLE_RAW.fed);
  const mx = readCsv(SAMPLE_RAW.banxico);
  const remit = readCsv(SAMPLE_RAW.remit);
  const events = JSON.parse(fs.readFileSync(SAMPLE_RAW.events, "utf8")).events || [];
  const holidays = JSON.parse(fs.readFileSync(SAMPLE_RAW.holidays, "utf8")).holidays || [];

  const fedMap = Object.fromEntries(fed.map((r) => [r.date, num(r.us_policy_rate)]));
  const mxMap = Object.fromEntries(mx.map((r) => [r.date, num(r.mx_policy_rate)]));
  const remitFilled = ffillQuarterly(
    fx.map((r) => r.date),
    remit.map((r) => ({
      date: r.date,
      remittance_cost_proxy: num(r.remittance_cost_proxy),
      fx_margin_pct: num(r.fx_margin_pct),
    }))
  );

  const spots = fx.map((r) => num(r.usd_mxn_spot));
  const rows = [];
  const vols = [];

  for (let i = 0; i < fx.length; i++) {
    const date = fx[i].date;
    const spot = spots[i];
    const prev = i > 0 ? spots[i - 1] : null;
    const prev5 = i >= 5 ? spots[i - 5] : null;
    const ret1 = prev ? (spot - prev) / prev : null;
    const ret5 = prev5 ? (spot - prev5) / prev5 : null;

    const rets = [];
    for (let j = Math.max(1, i - 19); j <= i; j++) {
      if (spots[j - 1]) rets.push((spots[j] - spots[j - 1]) / spots[j - 1]);
    }
    const vol =
      rets.length >= 10
        ? Math.sqrt(rets.reduce((s, r) => s + r * r, 0) / rets.length) * Math.sqrt(252)
        : null;
    vols.push(vol);

    const usRate = fedMap[date] ?? null;
    const mxRate = mxMap[date] ?? null;
    const diff = usRate != null && mxRate != null ? mxRate - usRate : null;
    const rem = remitFilled[i] || {};
    const spreadBps = rem.fx_margin_pct != null ? rem.fx_margin_pct * 10000 : null;
    const liq = vol != null && spreadBps != null ? Math.max(0, Math.min(1, 1 - (vol * 10 + spreadBps / 100) / 2)) : null;

    const ev = events.find((e) => e.date === date);
    const hol = holidays.find((h) => h.date === date);

    rows.push({
      date,
      usd_mxn_spot: spot?.toFixed(4),
      usd_return_1d: ret1 != null ? ret1.toFixed(6) : "",
      usd_return_5d: ret5 != null ? ret5.toFixed(6) : "",
      us_policy_rate: usRate?.toFixed(2) ?? "",
      mx_policy_rate: mxRate?.toFixed(2) ?? "",
      rate_differential: diff?.toFixed(2) ?? "",
      carry_proxy: diff?.toFixed(2) ?? "",
      volatility_20d: vol != null ? vol.toFixed(6) : "",
      volatility_regime: "",
      spread_proxy_bps: spreadBps != null ? spreadBps.toFixed(2) : "",
      event_flag: ev ? "true" : "false",
      event_description: ev?.description ?? "",
      holiday_flag: hol ? "true" : "false",
      holiday_description: hol?.description ?? "",
      liquidity_proxy: liq != null ? liq.toFixed(4) : "",
      remittance_cost_proxy: rem.remittance_cost_proxy != null ? rem.remittance_cost_proxy.toFixed(4) : "",
      data_mode: "synthetic",
      source_lineage: "sample_raw_v1|fx+fed+banxico+events+holidays+remit_cost",
    });
  }

  for (let i = 0; i < rows.length; i++) {
    rows[i].volatility_regime = volRegime(vols[i], vols);
  }

  const cols = [
    "date", "usd_mxn_spot", "usd_return_1d", "usd_return_5d", "us_policy_rate", "mx_policy_rate",
    "rate_differential", "carry_proxy", "volatility_20d", "volatility_regime", "spread_proxy_bps",
    "event_flag", "event_description", "holiday_flag", "holiday_description", "liquidity_proxy",
    "remittance_cost_proxy", "data_mode", "source_lineage",
  ];
  writeCsv(CANONICAL_SAMPLE, rows, cols);

  console.log("build_usd_mxn_sample_dataset PASS");
  console.log(JSON.stringify({
    rows: rows.length,
    date_min: rows[0]?.date,
    date_max: rows[rows.length - 1]?.date,
    data_mode: meta.data_mode,
    output: CANONICAL_SAMPLE,
  }, null, 2));
}

main();
