#!/usr/bin/env node
const path = require("path");
const { generateCorridorBrief } = require("../src/briefs/generate_corridor_brief");
const {
  MODEL_JSON,
  VALIDATION_JSON,
  VECTOR_STORE,
  BRIEF_MD,
  BRIEF_JSON,
} = require("../../scripts/lib/paths");

async function main() {
  const result = await generateCorridorBrief({
    modelPath: MODEL_JSON,
    validationPath: VALIDATION_JSON,
    vectorStorePath: VECTOR_STORE,
    outMd: BRIEF_MD,
    outJson: BRIEF_JSON,
  });
  console.log("run_corridor_brief PASS");
  console.log(JSON.stringify(result, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
