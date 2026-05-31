# Replication — Settlement Economics Lab

```bash
cd settlement_lab
source .venv/bin/activate
python scripts/reproduce_settlement_lab.py
```

## Pipeline order

1. `validate_settlement_data.py`
2. `build_settlement_dataset.py`
3. `run_settlement_indices.py`
4. `run_settlement_models.py`
5. `run_settlement_sensitivity.py`
6. `run_settlement_robustness.py`
7. `make_settlement_visuals.py`

## Expected outputs

| File | Description |
|------|-------------|
| `data/processed/*.csv` | Canonical tables |
| `data/outputs/settlement_drag_outputs.csv` | SDI results |
| `data/outputs/sensitivity_results.csv` | Sensitivity cases |
| `data/outputs/robustness_results.csv` | Robustness checks |
| `data/outputs/stress_scenario_results.csv` | PNF scenarios |
| `reports/figures/*.html` | Charts |

## Checksums

After adding raw files:
```bash
shasum -a 256 data/raw/**/*.csv
```

Record in `data/metadata/file_checksums.csv`.
