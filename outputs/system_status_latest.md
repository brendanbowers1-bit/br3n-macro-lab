# Bowers Frontier Macro Labs — System Status

Generated at: 2026-06-02T04:09:59.406Z
Environment: Node v25.9.0
Data mode: synthetic

## Pipeline Results
- dataset_build: **pass**
- validation: **pass**
- model_run: **pass**
- rag_ingest: **pass**
- brief_generation: **pass**
- eval_suite: **pass**

## Key Outputs
- canonical_dataset: OK
- validation_report: OK
- model_run: OK
- brief_md: OK
- brief_json: OK
- eval_report: OK
- vector_store: OK

## Corridor Risk Score
40.2/100 (Moderate)

## Warnings
- Validation completed with warnings (expected for synthetic data)
- LLM brief supplement unavailable: fetch failed

## Next Required Work
- Set BANXICO_SIE_TOKEN for official Banxico SIE series
- Replace synthetic sample with validated live lake outputs where appropriate
- Run model:smoke when Ollama/LM Studio available
- Expand eval live runs to full 25-question battery
