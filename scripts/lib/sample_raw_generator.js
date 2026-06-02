/** Generate clearly labeled synthetic USD/MXN sample raw files. */
const fs = require("fs");
const path = require("path");
const { writeCsv } = require("./csv_utils");
const { SAMPLE_RAW } = require("./paths");

function businessDays(start, count) {
  const out = [];
  const d = new Date(start + "T12:00:00Z");
  while (out.length < count) {
    const dow = d.getUTCDay();
    if (dow !== 0 && dow !== 6) out.push(d.toISOString().slice(0, 10));
    d.setUTCDate(d.getUTCDate() + 1);
  }
  return out;
}

function ensureSampleRawFiles() {
  const dates = businessDays("2024-01-02", 130);
  let spot = 17.05;
  const fxRows = dates.map((date, i) => {
    spot += (Math.sin(i / 8) * 0.02 + (Math.random() - 0.5) * 0.03);
    spot = Math.max(16.2, Math.min(18.5, spot));
    return { date, usd_mxn_spot: spot.toFixed(4), data_mode: "synthetic", source: "sample_generator_v1" };
  });
  writeCsv(SAMPLE_RAW.fx, fxRows, ["date", "usd_mxn_spot", "data_mode", "source"]);

  const fedRate = 5.25;
  writeCsv(
    SAMPLE_RAW.fed,
    dates.map((date) => ({ date, us_policy_rate: fedRate.toFixed(2), data_mode: "synthetic" })),
    ["date", "us_policy_rate", "data_mode"]
  );

  let mxRate = 11.25;
  const banxicoRows = dates.map((date, i) => {
    if (i > 0 && i % 45 === 0) mxRate = Math.max(9.5, mxRate - 0.25);
    return { date, mx_policy_rate: mxRate.toFixed(2), data_mode: "synthetic" };
  });
  writeCsv(SAMPLE_RAW.banxico, banxicoRows, ["date", "mx_policy_rate", "data_mode"]);

  const events = [
    { date: "2024-03-20", event_type: "FOMC", description: "Sample FOMC decision window", data_mode: "synthetic" },
    { date: "2024-05-09", event_type: "Banxico", description: "Sample Banxico policy meeting", data_mode: "synthetic" },
    { date: "2024-09-18", event_type: "FOMC", description: "Sample FOMC decision window", data_mode: "synthetic" },
    { date: "2024-11-14", event_type: "Banxico", description: "Sample Banxico policy meeting", data_mode: "synthetic" },
  ];
  fs.mkdirSync(path.dirname(SAMPLE_RAW.events), { recursive: true });
  fs.writeFileSync(SAMPLE_RAW.events, JSON.stringify({ events, data_mode: "synthetic" }, null, 2));

  const holidays = [
    { date: "2024-01-01", country: "US/MX", description: "New Year (sample)", data_mode: "synthetic" },
    { date: "2024-07-04", country: "US", description: "US Independence Day (sample)", data_mode: "synthetic" },
    { date: "2024-09-16", country: "MX", description: "Mexico Independence Day (sample)", data_mode: "synthetic" },
    { date: "2024-12-25", country: "US/MX", description: "Christmas (sample)", data_mode: "synthetic" },
  ];
  fs.mkdirSync(path.dirname(SAMPLE_RAW.holidays), { recursive: true });
  fs.writeFileSync(SAMPLE_RAW.holidays, JSON.stringify({ holidays, data_mode: "synthetic" }, null, 2));

  writeCsv(
    SAMPLE_RAW.remit,
    [
      { date: "2024-01-01", remittance_cost_proxy: "0.048", fee_pct: "0.012", fx_margin_pct: "0.028", data_mode: "synthetic" },
      { date: "2024-04-01", remittance_cost_proxy: "0.045", fee_pct: "0.011", fx_margin_pct: "0.026", data_mode: "synthetic" },
      { date: "2024-07-01", remittance_cost_proxy: "0.043", fee_pct: "0.010", fx_margin_pct: "0.025", data_mode: "synthetic" },
      { date: "2024-10-01", remittance_cost_proxy: "0.041", fee_pct: "0.009", fx_margin_pct: "0.024", data_mode: "synthetic" },
    ],
    ["date", "remittance_cost_proxy", "fee_pct", "fx_margin_pct", "data_mode"]
  );

  return { dates: dates.length, data_mode: "synthetic" };
}

module.exports = { ensureSampleRawFiles, businessDays };
