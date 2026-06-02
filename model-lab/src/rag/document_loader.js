const fs = require("fs");
const path = require("path");

function loadDocuments(rootDir) {
  const docs = [];
  if (!fs.existsSync(rootDir)) return docs;
  for (const file of fs.readdirSync(rootDir)) {
    const fp = path.join(rootDir, file);
    if (!fs.statSync(fp).isFile()) continue;
    const ext = path.extname(file).toLowerCase();
    if (![".md", ".txt", ".json"].includes(ext)) continue;
    docs.push({
      id: file,
      source: file,
      text: fs.readFileSync(fp, "utf8"),
      type: ext.slice(1),
    });
  }
  return docs;
}

module.exports = { loadDocuments };
