#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const { runEvals } = require("../src/evals/run_evals");
const { MODEL_JSON, EVAL_JSON, EVAL_MD } = require("../../scripts/lib/paths");

async function main() {
  const report = await runEvals({ modelRunPath: MODEL_JSON });
  fs.mkdirSync(path.dirname(EVAL_JSON), { recursive: true });
  fs.writeFileSync(EVAL_JSON, JSON.stringify(report, null, 2));

  const md = `# Bowers Frontier Macro Labs — Model Eval Report

Provider: ${report.provider}
Provider status: ${report.provider_status}
Questions defined: ${report.question_count}
Live runs: ${report.questions_run_live}
Generated: ${report.generated_at}

## Scoring dimensions
${report.scoring_schema.dimensions.map((d) => `- ${d}: ${report.scoring_schema.rubric[d]}`).join("\n")}

## Live results
${report.results.length ? report.results.map((r) => `### ${r.id}\nQ: ${r.question}\n${r.answer ? `A: ${r.answer.slice(0, 400)}...` : `Error: ${r.error}`}`).join("\n\n") : "No live provider — eval questions ready in eval_questions.js"}

## Note
${report.note}
`;
  fs.writeFileSync(EVAL_MD, md);
  console.log("run_evals PASS");
  console.log(JSON.stringify({ provider_status: report.provider_status, live: report.questions_run_live }, null, 2));
}

main();
