# Connector Governance

1. **Never overwrite raw data** — append dated immutable files.
2. **Store retrieval timestamp** in sidecar `.meta.json`.
3. **Store source reference** in `source_registry.json` and `data_catalog.json`.
4. **Validate every pull** before processed merge.
5. **Fail closed** if data quality is poor.
6. **Dashboard stale warnings** when `retrieval_date` exceeds threshold.
7. **No live claims** unless connector succeeded and validation passed.
8. **No financial advice** in connector-driven UI copy.
