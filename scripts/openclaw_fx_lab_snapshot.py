#!/usr/bin/env python3
"""
Compact FX Lab status for OpenClaw (iMessage / gateway agent).

Usage:
  python scripts/openclaw_fx_lab_snapshot.py
  python scripts/openclaw_fx_lab_snapshot.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data" / "outputs"
PROC = ROOT / "data" / "processed"


def _read_csv(name: str):
    p = OUT / name
    if not p.exists():
        return None
    import pandas as pd

    return pd.read_csv(p)


def build_snapshot() -> dict:
    snap: dict = {
        "project": "Bowers Frontier Macro Labs — FX Lab",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(ROOT),
        "disclaimer": "Research only. Not investment advice. No live trading.",
    }

    flow = PROC / "usdmxn_features_regimes_flow.csv"
    base = PROC / "usdmxn_features_regimes.csv"
    data_path = flow if flow.exists() else base
    if data_path.exists():
        import pandas as pd

        df = pd.read_csv(data_path, parse_dates=["date"])
        last = df.iloc[-1]
        snap["data"] = {
            "file": data_path.name,
            "rows": len(df),
            "last_date": str(df["date"].max().date()),
            "price": float(last.get("price", 0)),
            "regime": str(last.get("regime", "")),
        }
    else:
        snap["data"] = {"error": "Run python scripts/run_usdmxn_backtest.py first"}

    fc = _read_csv("model_zoo_forecast_scorecard.csv")
    if fc is not None and not fc.empty:
        beats_rmse = int(fc["model_beats_rw_rmse"].sum())
        beats_mae = int(fc["model_beats_rw_mae"].sum())
        best_rmse = fc.sort_values("rmse_model").iloc[0]["model_name"]
        snap["model_zoo_forecast"] = {
            "models": len(fc),
            "beat_random_walk_rmse": beats_rmse,
            "beat_random_walk_mae": beats_mae,
            "lowest_rmse_model": str(best_rmse),
        }

    tr = _read_csv("model_zoo_trading_scorecard.csv")
    if tr is not None and not tr.empty and "sharpe_net" in tr.columns:
        best = tr.sort_values("sharpe_net", ascending=False).iloc[0]
        snap["model_zoo_trading"] = {
            "best_model": str(best["model_name"]),
            "best_sharpe_net": float(best["sharpe_net"]),
        }

    hg = _read_csv("model_zoo_hedge_scorecard.csv")
    if hg is not None and not hg.empty:
        best = hg.sort_values("cost_adjusted_risk_reduction", ascending=False).iloc[0]
        snap["model_zoo_hedge"] = {
            "best_model": str(best["model_name"]),
            "cost_adjusted_risk_reduction": float(best["cost_adjusted_risk_reduction"]),
        }

    log = _read_csv("model_zoo_run_log.csv")
    if log is not None and not log.empty:
        snap["model_zoo_run"] = {
            "attempted": len(log),
            "successful": int((log["status"] == "success").sum()),
            "skipped": int((log["status"] == "skipped").sum()),
        }

    snap["public_site"] = "https://brendanbowers1-bit.github.io/br3n-macro-lab/"
    snap["openclaw_skill"] = str(ROOT / "openclaw/skills/fx-lab/SKILL.md")
    return snap


def main() -> None:
    parser = argparse.ArgumentParser(description="FX Lab snapshot for OpenClaw")
    parser.add_argument("--json", action="store_true", help="Print JSON only")
    args = parser.parse_args()

    snap = build_snapshot()

    if args.json:
        print(json.dumps(snap, indent=2))
        return

    d = snap.get("data", {})
    print("Bowers Frontier Macro Labs — FX Lab snapshot")
    print(f"Generated: {snap['generated_at']}")
    print()
    if "regime" in d:
        print(f"USD/MXN: {d.get('price')} | regime {d.get('regime')} | as of {d.get('last_date')}")
    else:
        print(f"Data: {d.get('error', 'unknown')}")
    if "model_zoo_forecast" in snap:
        f = snap["model_zoo_forecast"]
        print(f"Forecast: {f['beat_random_walk_rmse']} models beat RW (RMSE); lowest RMSE: {f['lowest_rmse_model']}")
    if "model_zoo_trading" in snap:
        t = snap["model_zoo_trading"]
        print(f"Trading: best {t['best_model']} (Sharpe net {t['best_sharpe_net']})")
    if "model_zoo_hedge" in snap:
        h = snap["model_zoo_hedge"]
        print(f"Hedge: best {h['best_model']} (cost-adj risk reduction {h['cost_adjusted_risk_reduction']})")
    print()
    print(snap["disclaimer"])


if __name__ == "__main__":
    main()
