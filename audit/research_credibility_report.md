# Research Credibility Report

**Generated:** 2026-06-01T02:46:02.547480+00:00

## Quality run summary

- PASS: 5
- FAIL: 2
- WARNING: 0
- SKIPPED: 6

## Publication-grade checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | No mock data in final outputs | Manual review required |
| 2 | Tier 1/2 sources for core variables | See DATA_GOVERNANCE / data_validation |
| 3 | Raw file hashes recorded | settlement_lab/metadata |
| 4 | Methodology version recorded | lineage columns |
| 5 | Assumptions disclosed | working papers / limitations |
| 6 | Sensitivity analysis completed | sensitivity_results.csv |
| 7 | Robustness checks completed | robustness_results.csv |
| 8 | Model validation passed | model_validation_report |
| 9 | Data validation passed | data_validation_report |
| 10 | Reproduction script passed | reproduce steps in quality report |
| 11 | Data quality score above 80 | dashboard / outputs |
| 12 | Claims limited to evidence | no causal language without identification |

## Failures

- data_validation: {"pass": 6, "fail": 20, "warning": 0, "total": 26}
- model_validation: {"pass": 3, "fail": 2, "skipped": 0}
