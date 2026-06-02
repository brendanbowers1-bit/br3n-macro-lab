#!/usr/bin/env node
const path = require("path");
const { buildStore, REF_DIR } = require("../src/rag/rag_pipeline");
const { VECTOR_STORE } = require("../../scripts/lib/paths");

function main() {
  const store = buildStore(REF_DIR);
  store.save(VECTOR_STORE);
  console.log("ingest_documents PASS");
  console.log(JSON.stringify({ chunks: store.chunks.length, output: VECTOR_STORE }, null, 2));
}

main();
