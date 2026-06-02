const path = require("path");
const { loadDocuments } = require("./document_loader");
const { chunkAll } = require("./chunker");
const { SimpleVectorStore } = require("./simple_vector_store");
const { retrieve } = require("./retriever");

const REF_DIR = path.join(__dirname, "../../data/reference");

function buildStore(refDir = REF_DIR) {
  const docs = loadDocuments(refDir);
  const chunks = chunkAll(docs);
  return SimpleVectorStore.fromChunks(chunks);
}

function ragContext(query, store, k = 4) {
  const hits = retrieve(store, query, k);
  return {
    query,
    chunks: hits,
    context_text: hits.map((h) => `[${h.source}] ${h.text}`).join("\n\n"),
  };
}

module.exports = { buildStore, ragContext, REF_DIR };
