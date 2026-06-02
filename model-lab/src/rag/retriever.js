const { tokenize } = require("./simple_vector_store");

function scoreQuery(query, chunk) {
  const q = new Set(tokenize(query));
  const terms = tokenize(chunk.text);
  let hits = 0;
  for (const t of terms) if (q.has(t)) hits++;
  return hits;
}

function retrieve(store, query, k = 4) {
  const ranked = store.chunks
    .map((c) => ({ ...c, score: scoreQuery(query, c) }))
    .filter((c) => c.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, k);
  return ranked;
}

module.exports = { retrieve };
