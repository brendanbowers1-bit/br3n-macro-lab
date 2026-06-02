# RAG Methodology

Bowers Frontier Macro Labs uses a **local keyword/BM25-style baseline** (`model-lab/src/rag/`).

- Retrieves chunks from `model-lab/data/reference/`
- Output: `model-lab/outputs/vector_store.json`
- RAG explains research context — **does not create market facts**
- Upgrade path: Chroma, LanceDB, Qdrant, FAISS, pgvector

Run: `npm run model:ingest`
