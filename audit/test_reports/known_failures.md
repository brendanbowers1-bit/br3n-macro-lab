# Known Failures and Limitations (Quality System)

**Updated:** 2026-05-31

## Data validation (expected until publication-grade data only)

- **20 CSV checks fail** in the latest run — mostly mock/demo rows with `data_quality_score > 30`, missing metadata columns on legacy outputs, or settlement demo tables. This is **by design** under the non-negotiable rules until Tier-1-only outputs are enforced.
- Re-run: `python scripts/validate_all_data.py` — review `audit/data_quality_reports/data_validation_report.md`.

## Model validation

- Some settlement output CSVs may be **empty placeholders** (`No columns to parse from file`) until the settlement pipeline is run: `cd settlement_lab && PYTHONPATH=. python scripts/reproduce_settlement_lab.py`.

## Quality runner timing

- **Smoke tests** (`scripts/smoke_test.py`, settlement smoke) rebuild full datasets and can take **5–15 minutes**. The default `run_all_quality_checks.py` marks them **SKIPPED**; run manually: `python scripts/smoke_test.py`.
- **Full reproduction** is **SKIPPED** by default. Use `python scripts/reproduce_all.py` or `python scripts/run_all_quality_checks.py --include-reproduce` (slow).
- **Settlement pytest** must run with `PYTHONPATH=.` from `settlement_lab/` (see `Makefile` `test` target). Combined root+settlement pytest from repo root causes `src` import collisions.

## Dependencies

- `tabulate` is **not required** — reporting uses plain Markdown tables. Older runs may show tabulate errors in archived reports.

## Line count

- Excludes `data/raw/`, `data/processed/`, `data/outputs/`, and settlement data folders. Latest count: **~515 files, ~102k lines, ~93k code lines** (see `audit/project_metrics/line_count_report.md`).

## Time tracking

- Historical time before this tracker was installed **cannot be measured exactly**. Use `python scripts/estimate_time_from_git.py` for **estimated** hours from commit timestamps (labeled as estimate).

## Snapshots

- Zip step may warn on duplicate `settlement_lab/requirements.txt` path — harmless; snapshot still created.

## OpenSSL warning

- `urllib3` LibreSSL warning on macOS system Python — informational only.
