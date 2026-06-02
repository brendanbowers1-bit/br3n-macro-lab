function chunkDocument(doc, chunkSize = 800, overlap = 100) {
  const text = doc.text.replace(/\r\n/g, "\n");
  const chunks = [];
  let i = 0;
  let idx = 0;
  while (i < text.length) {
    const slice = text.slice(i, i + chunkSize);
    chunks.push({
      chunk_id: `${doc.id}#${idx}`,
      source: doc.source,
      text: slice.trim(),
    });
    i += chunkSize - overlap;
    idx++;
  }
  return chunks;
}

function chunkAll(documents) {
  return documents.flatMap((d) => chunkDocument(d));
}

module.exports = { chunkAll };
