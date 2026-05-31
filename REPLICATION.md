# Replication Package — BR3N Value Survival Index

Reproduce corridor-level Value Survival Index outputs from raw public data.

**Research-only. Not investment advice.**

---

## Software environment

- **Python:** 3.11+ recommended
- **Virtual env:** `python -m venv .venv && source .venv/bin/activate`
- **Dependencies:** `pip install -r requirements.txt`

Key packages: `pandas`, `numpy`, `plotly`, `streamlit`, `statsmodels` (optional, for regressions).

---

## Data folder structure

```
data/
  raw/
    world_bank_rpw/          # RPW corridor costs
    world_bank_knomad/       # Bilateral remittance flows
    imf/                     # FX rates, macro indicators
    bis/                     # FX turnover (triennial)
    fred/                    # DXY for event studies
    manual/                  # Sovereignty, wages (labeled manual)
  processed/                 # Built canonical tables
  outputs/                   # VSI, sensitivity, robustness CSVs
reports/
  figures/                   # PNG/HTML charts
  working_paper/             # Academic draft sections
```

---

## Raw data acquisition

1. **RPW:** Download from https://remittanceprices.worldbank.org/ → place in `data/raw/world_bank_rpw/`  
   Minimum: `rpw_historical_panel.csv` (included in repo).

2. **KNOMAD:** Bilateral matrix → `data/raw/world_bank_knomad/bilateral_remittances.csv`

3. **IMF FX:** Lab cache or IMF API → `data/raw/imf/fx_rates_from_lab.csv`

4. **World Bank macro:** API cache → `data/raw/imf/macro_indicators_wb_api.csv`

5. **BIS:** Triennial survey CSV → `data/raw/bis/fx_turnover_2022.csv`

6. **FRED DXY:** `data/raw/fred/dxy_daily.csv` (for event studies)

---

## Exact scripts to run

```bash
cd fx_regime_lab
source .venv/bin/activate

# Full pipeline
python scripts/reproduce_all.py

# Or step-by-step:
python scripts/build_dataset.py
python scripts/run_vsi.py
python scripts/run_sensitivity.py
python scripts/run_robustness.py
python scripts/make_visuals.py
python scripts/smoke_test.py

# Interactive dashboard
streamlit run src/dashboard/app.py
```

---

## Expected outputs

| File | Description |
|------|-------------|
| `data/processed/value_survival_outputs.csv` | Full VSI panel with traceability |
| `data/outputs/value_survival_outputs.csv` | Published VSI copy |
| `data/outputs/vsi_sensitivity_results.csv` | Conservative/baseline/severe cases |
| `data/outputs/robustness_results.csv` | Specification robustness checks |
| `reports/figures/vsi_*.png` | Ranked bars, breakdowns, quality scores |
| `reports/figures/vsi_corridor_summary.csv` | Corridor summary table |

---

## Checksums (placeholder)

After downloading fresh raw data, record SHA-256 checksums:

```bash
shasum -a 256 data/raw/world_bank_rpw/*.csv
shasum -a 256 data/raw/world_bank_knomad/*.csv
```

*(Populate checksums when pinning a publication snapshot.)*

---

## Reproduce figures

`scripts/make_visuals.py` writes to `reports/figures/`. Requires `plotly`; PNG export optional via `kaleido`.

---

## Known limitations

- Full RPW Excel not required but improves fee/margin coverage.
- Timing, volatility, payout, trust, and dollar-drag components include **transparent assumptions**.
- Extended VSI (trust + dollar drag) is labeled separately from baseline VSI_CORE.
- Mock/demo mode activates if raw files missing — **large visible warning** in dashboard.
- Panel regressions output "Insufficient official data" when N is small or mock flag is set.

---

## Methodology version

Current: `vsi-credible-1.0` (see `src/config/research_settings.py`).
