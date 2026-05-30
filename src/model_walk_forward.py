"""
Walk-forward testing for the model zoo.

Train windows inform simple models (e.g. flow bias); test windows score performance.
Research only — no tuning on test data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from .backtest import generate_walk_forward_folds
from .model_evaluation import (
    evaluate_forecast_model,
    evaluate_hedge_model,
    evaluate_trading_model,
)
from .model_zoo import run_model_zoo


def run_model_zoo_walk_forward(
    df: pd.DataFrame,
    cfg: dict,
    model_names: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Walk-forward OOS evaluation for each model.

    Returns (scorecard, detail) dataframes saved to data/outputs/.
    """
    mz = cfg.get("model_zoo", {})
    if not mz.get("walk_forward_enabled", cfg["backtest"].get("walk_forward_enabled", True)):
        return pd.DataFrame(), pd.DataFrame()

    folds = generate_walk_forward_folds(df.index, cfg)
    detail_rows: List[dict] = []

    for fold in folds:
        train = df.loc[(df.index >= fold.train_start) & (df.index <= fold.train_end)]
        test = df.loc[(df.index >= fold.test_start) & (df.index <= fold.test_end)]
        if len(test) < 30 or len(train) < 60:
            continue

        outputs, _ = run_model_zoo(test, cfg, model_names=model_names, train_df=train)

        for name, output in outputs.items():
            mtype = output["model_type"].iloc[0]
            row = {
                "model_name": name,
                "window_start": fold.test_start.date().isoformat(),
                "window_end": fold.test_end.date().isoformat(),
                "model_type": mtype,
                "observations": len(test),
            }

            fc = evaluate_forecast_model(test, output)
            row.update(
                {
                    "rmse_model": fc["rmse_model"],
                    "rmse_random_walk": fc["rmse_random_walk"],
                    "mae_model": fc["mae_model"],
                    "mae_random_walk": fc["mae_random_walk"],
                }
            )

            if mtype in ("trading", "hybrid", "forecast"):
                tr = evaluate_trading_model(test, output, cfg)
                row.update(
                    {
                        "total_return_net": tr["total_return_net"],
                        "sharpe_net": tr["sharpe_net"],
                        "max_drawdown_net": tr["max_drawdown_net"],
                    }
                )
            else:
                row.update({"total_return_net": None, "sharpe_net": None, "max_drawdown_net": None})

            if output["hedge_ratio"].notna().any():
                hg = evaluate_hedge_model(test, output, cfg)
                row["hedge_volatility_reduction"] = hg["volatility_reduction"]
            else:
                row["hedge_volatility_reduction"] = None

            detail_rows.append(row)

    detail = pd.DataFrame(detail_rows)
    if detail.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Aggregate scorecard: mean metrics per model
    agg_cols = [
        "total_return_net",
        "sharpe_net",
        "max_drawdown_net",
        "rmse_model",
        "rmse_random_walk",
        "mae_model",
        "mae_random_walk",
        "hedge_volatility_reduction",
    ]
    scorecard = (
        detail.groupby(["model_name", "model_type"], as_index=False)
        .agg({c: "mean" for c in agg_cols if c in detail.columns})
        .round(4)
    )
    scorecard["windows_tested"] = detail.groupby("model_name").size().reindex(scorecard["model_name"]).values

    out_dir = Path(cfg.get("reporting", {}).get("output_dir", "data/outputs"))
    if not out_dir.is_absolute():
        out_dir = Path(__file__).resolve().parents[1] / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    scorecard.to_csv(out_dir / "model_zoo_walk_forward_scorecard.csv", index=False)
    detail.to_csv(out_dir / "model_zoo_walk_forward_detail.csv", index=False)

    return scorecard, detail
