# Replication — Stablecoin Settlement Window Lab

```bash
cd stablecoin_lab
source .venv/bin/activate
python scripts/reproduce_stablecoin_lab.py
```

## Pipeline order

1. `validate_stablecoin_data.py`
2. `build_stablecoin_dataset.py`
3. `run_stablecoin_indices.py`
4. `run_stablecoin_models.py`
5. `run_stablecoin_sensitivity.py`
6. `run_stablecoin_robustness.py`
7. `make_stablecoin_visuals.py`

## Expected outputs

| File | Description |
|------|-------------|
| `data/processed/*.csv` | Canonical cleaned tables |
| `data/outputs/stablecoin_finality_quality_outputs.csv` | SFQI results |
| `data/outputs/settlement_window_compression_outputs.csv` | SWC results |
| `data/outputs/liquidity_transformation_outputs.csv` | SLT results |
| `data/outputs/digital_run_velocity_outputs.csv` | DRV results |
| `data/outputs/stablecoin_dollarization_outputs.csv` | Dollarization index |
| `data/outputs/tokenized_money_singleness_outputs.csv` | Singleness index |
| `data/outputs/compliance_settlement_drag_outputs.csv` | Compliance drag |
| `data/outputs/stablecoin_value_survival_outputs.csv` | SVSI results |
| `data/outputs/sensitivity_results.csv` | Sensitivity cases |
| `data/outputs/robustness_results.csv` | Robustness checks |
| `data/outputs/validation_summary.csv` | Validation summary |
| `data/outputs/provenance_summary.csv` | Mock/mixed mode flags |
| `reports/figures/*.png` | Charts |

## Tests

```bash
cd stablecoin_lab
pytest tests/ -q
python scripts/smoke_test_stablecoin_lab.py
```

## Dashboard

```bash
streamlit run src/dashboard/app.py
```

## Checksums

After adding raw files:

```bash
shasum -a 256 data/raw/**/*.csv
```

Record in `data/metadata/file_checksums.csv`.

## Publication-grade checklist

1. No mock data in final outputs
2. Tier 1/Tier 2 sources for core variables
3. Reserve data from issuer attestations/public filings
4. Price/peg data from reliable market source
5. Chain fee/finality assumptions documented
6. Off-ramp assumptions verified
7. All assumptions sensitivity-tested
8. Robustness checks completed
9. Raw files archived and hashed
10. Replication script runs end-to-end
11. Claims limited to evidence
