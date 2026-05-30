"""
Generate markdown report from model-zoo scorecards.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from . import LAB_NAME


def _read_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def _table(df: pd.DataFrame, cols: Optional[list] = None, max_rows: int = 20) -> str:
    if df.empty:
        return "_No data._\n"
    use = df[cols] if cols else df
    use = use.head(max_rows)
    headers = list(use.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for _, row in use.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in headers) + " |")
    return "\n".join(lines) + "\n"


def generate_model_zoo_report(root: Optional[Path] = None) -> Path:
    """Build reports/model_zoo_report.md from scorecard CSVs."""
    root = root or Path(__file__).resolve().parents[1]
    out_dir = root / "data" / "outputs"
    report_dir = root / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    run_log = _read_csv(out_dir / "model_zoo_run_log.csv")
    fc = _read_csv(out_dir / "model_zoo_forecast_scorecard.csv")
    tr = _read_csv(out_dir / "model_zoo_trading_scorecard.csv")
    hg = _read_csv(out_dir / "model_zoo_hedge_scorecard.csv")
    wf = _read_csv(out_dir / "model_zoo_walk_forward_scorecard.csv")

    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    attempted = len(run_log)
    success = int((run_log["status"] == "success").sum()) if not run_log.empty else 0
    skipped = int((run_log["status"] == "skipped").sum()) if not run_log.empty else 0

    tested = run_log["model_name"].tolist() if not run_log.empty else []

    # What worked / failed heuristics
    worked: list[str] = []
    failed: list[str] = []

    if not fc.empty:
        if fc["model_beats_rw_rmse"].any():
            worked.append("At least one model beats random walk by RMSE on full sample")
        else:
            failed.append("No model beats random walk by RMSE")
        if fc["model_beats_rw_mae"].any():
            worked.append("At least one model beats random walk by MAE on full sample")
        else:
            failed.append("No model beats random walk by MAE")

    if not tr.empty and "sharpe_net" in tr.columns:
        best = tr.sort_values("sharpe_net", ascending=False).iloc[0]
        worked.append(f"Best net Sharpe: {best['model_name']} ({best['sharpe_net']})")
        if tr["sharpe_net"].max() <= 0:
            failed.append("No trading model with positive net Sharpe")

    if not hg.empty:
        best_h = hg.sort_values("cost_adjusted_risk_reduction", ascending=False).iloc[0]
        worked.append(
            f"Best hedge cost-adj risk reduction: {best_h['model_name']} "
            f"({best_h['cost_adjusted_risk_reduction']})"
        )

    md = f"""# {LAB_NAME} — Model Zoo Report

**Generated:** {ts}

> Research and education only. Not investment advice. No guaranteed returns. No live trading.

The model zoo is designed to prevent overreliance on a single rule. The objective is **not** to find one perfect FX predictor, but to test whether different model families provide value under different regimes and decision contexts.

This tests **conditional forecastability** — not proof that FX is predictable.

---

## 1. Purpose

Compare simple, explainable models against random walk, buy-and-hold, and always-flat benchmarks under transaction costs, walk-forward splits, and separate forecast / trading / hedge-governance lenses.

---

## 2. Models tested

- **Attempted:** {attempted}
- **Successful:** {success}
- **Skipped:** {skipped}

"""
    if tested:
        md += "\n".join(f"- {m}" for m in tested) + "\n"

    if not run_log.empty:
        md += "\n### Run log\n\n"
        md += _table(run_log, ["model_name", "status", "reason", "required_columns_missing"])

    md += """
---

## 3. Forecast accuracy results

"""
    if not fc.empty:
        md += _table(
            fc,
            [
                "model_name",
                "rmse_model",
                "rmse_random_walk",
                "mae_model",
                "mae_random_walk",
                "model_beats_rw_rmse",
                "model_beats_rw_mae",
                "directional_accuracy",
            ],
        )
    else:
        md += "_Run `python scripts/run_model_zoo.py` first._\n"

    md += """
---

## 4. Trading P&L results

"""
    if not tr.empty:
        md += _table(
            tr,
            [
                "model_name",
                "total_return_net",
                "sharpe_net",
                "max_drawdown_net",
                "number_of_trades",
                "total_transaction_cost",
                "percent_time_in_market",
            ],
        )
    else:
        md += "_No trading scorecard._\n"

    md += """
---

## 5. Hedge-governance results

"""
    if not hg.empty:
        md += _table(
            hg,
            [
                "model_name",
                "volatility_reduction",
                "hedge_turnover",
                "total_hedge_cost",
                "cost_adjusted_risk_reduction",
                "average_hedge_ratio",
                "regret_proxy",
            ],
        )
    else:
        md += "_No hedge scorecard._\n"

    md += """
---

## 6. Walk-forward results

"""
    if not wf.empty:
        md += _table(wf)
    else:
        md += "_Walk-forward not run or no folds._\n"

    md += """
---

## 7. What worked

"""
    md += "\n".join(f"- {w}" for w in worked) if worked else "- _See scorecards above._\n"

    md += """
---

## 8. What failed

"""
    md += "\n".join(f"- {f}" for f in failed) if failed else "- _See scorecards above._\n"

    md += """
---

## 9. Data limitations

- Results depend on data quality (Tier 1 spot preferred; yfinance fallback possible).
- Macro / flow columns may be missing on base feature files — some models skip gracefully.
- Full-sample metrics can overstate edge; prefer walk-forward and random-walk comparisons.
- Hedge metrics use simplified exposure math, not ASC 815 / IFRS 9 effectiveness testing.

---

## 10. Next model candidates

- Regime-switching forecast combinations with strict holdout discipline
- Vol-scaled position sizing (not binary ±1)
- Corridor-specific flow models with longer history
- Cost-aware ensemble with veto rules
- Hedge policies with explicit turnover caps

---

## Commands

```bash
python scripts/run_model_zoo.py
python scripts/generate_model_zoo_report.py
```
"""

    path = report_dir / "model_zoo_report.md"
    path.write_text(md, encoding="utf-8")
    return path
