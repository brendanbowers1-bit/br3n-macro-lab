#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const { validateDataset } = require("../src/data/validate_dataset");
const { CANONICAL_SAMPLE, VALIDATION_JSON, VALIDATION_MD } = require("./lib/paths");

function main() {
  const report = validateDataset(CANONICAL_SAMPLE);
  fs.mkdirSync(path.dirname(VALIDATION_JSON), { recursive: true });
  fs.writeFileSync(VALIDATION_JSON, JSON.stringify(report, null, 2));

  const md = `# USD/MXN Dataset Validation Report

Status: **${report.status}**

Dataset: \`${CANONICAL_SAMPLE}\`
Rows: ${report.rows}
Date range: ${report.date_min} → ${report.date_max}
Data mode: ${report.data_mode}
Generated at: ${report.generated_at}

## Checks
${report.checks.map((c) => `- **${c.id}**: ${c.status}${c.message ? ` — ${c.message}` : ""}`).join("\n")}

## Warnings
${report.checks.filter((c) => c.status === "warn").map((c) => `- ${c.id}: ${c.message || ""}`).join("\n") || "None"}

> Research dataset. Synthetic/sample data is clearly labeled. Not financial advice.
`;
  fs.writeFileSync(VALIDATION_MD, md);

  console.log(`validate_usd_mxn_dataset ${report.status.toUpperCase()}`);
  if (report.status === "Fail") process.exit(1);
}

main();
