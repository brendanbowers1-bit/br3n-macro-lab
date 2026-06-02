const fs = require("fs");
const path = require("path");

function tokenize(text) {
  return text.toLowerCase().split(/[^a-z0-9]+/).filter((t) => t.length > 2);
}

class SimpleVectorStore {
  constructor(chunks = []) {
    this.chunks = chunks;
  }

  static fromChunks(chunks) {
    return new SimpleVectorStore(chunks);
  }

  save(filePath) {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(
      filePath,
      JSON.stringify({ version: "1", engine: "keyword_bm25_baseline", chunks: this.chunks }, null, 2)
    );
  }

  static load(filePath) {
    if (!fs.existsSync(filePath)) return new SimpleVectorStore([]);
    const data = JSON.parse(fs.readFileSync(filePath, "utf8"));
    return new SimpleVectorStore(data.chunks || []);
  }
}

module.exports = { SimpleVectorStore, tokenize };
