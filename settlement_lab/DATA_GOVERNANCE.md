# Data Governance — Settlement Economics Lab

## Rule: NO_UNLABELED_DATA = True

No model output may appear without full data lineage. Validation fails if required metadata is missing.

## Required metadata (every row)

`source_name`, `source_url_or_reference`, `data_provider`, `extraction_date`, `methodology_version`, `raw_file_name`, `raw_file_hash_sha256`, `transformation_script`, `observed_vs_estimated_flag`, `official_vs_manual_flag`, `mock_data_flag`, `data_quality_score`, `data_quality_grade`

## Credibility tiers

| Tier | Source type | Max credibility points |
|------|-------------|------------------------|
| 1 | BIS, IMF, World Bank, central banks | 20 |
| 2 | Regulated public filings | 16 |
| 3 | Reputable industry reports | 12 |
| 4 | Manual expert assumptions | 6 |
| 5 | Mock/demo | 0 (cap score at 30) |

## Grades (0–100)

- 90–100: Publication grade
- 80–89: Research grade
- 70–79: Strong preliminary
- 60–69: Exploratory
- 40–59: Demo/weak
- below 40: Do not use for inference

## Imputation policy

- Do not silently fill missing data
- Label all imputation with `imputation_flag=True`
- Run sensitivity analysis on imputed fields

## Mock data policy

- `mock_data_flag=True` on all synthetic rows
- `source_id=MOCK_DEMO_ONLY`
- `data_quality_score ≤ 30`
- Giant dashboard warning required
