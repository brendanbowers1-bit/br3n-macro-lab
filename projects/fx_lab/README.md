# FX Lab

**Vertical:** Markets · Currency regime intelligence

## Mission

Study when currency markets become less random and how regime intelligence can improve FX research, payment-corridor risk analysis, and treasury hedge governance.

## Research Questions

- When does random walk fail in FX?
- When are currencies conditionally forecastable?
- Can regime models improve hedge discipline even when forecasts are weak?
- Do payment corridors show flow-pressure behavior?
- When should a desk avoid hedge over-adjustment?

## Outputs

- FX regime dashboard (`src/luxury_dashboard.py`, `src/dashboard.py`)
- Random-walk and academic tests
- Remittance corridor roadmap
- Hedge governance scorecards
- FX desk command center
- Model cards, data-quality reports, publication memos

## Status

**Active** — prototype and research platform. Primary codebase lives in this repository root.

## Run

```bash
cd ~/fx_regime_lab
source .venv/bin/activate
python scripts/run_usdmxn_backtest.py
python scripts/run_corridor_roadmap.py
python scripts/run_fx_desk_framework.py
streamlit run src/luxury_dashboard.py
```

## Disclaimer

FX Lab research is for education, analysis, and risk-framing only. Not investment advice. No live trading.
