#!/usr/bin/env python3
"""
Create a dated research snapshot archive.

Usage:
  python scripts/create_research_snapshot.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SNAPSHOTS = ROOT / "research_snapshots"


def _git_hash() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return r.stdout.strip()
    except Exception:
        return "unavailable"


def _copy_tree(src: Path, dst: Path) -> list[str]:
    copied: list[str] = []
    if not src.exists():
        return copied
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(str(dst.relative_to(ROOT)))
        return copied
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.rglob("*"):
        if item.is_file():
            rel = item.relative_to(src)
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            copied.append(str(target.relative_to(ROOT)))
    return copied


def _read_regime() -> str:
    for name in ("usdmxn_features_regimes_flow.csv", "usdmxn_features_regimes.csv"):
        p = ROOT / "data/processed" / name
        if not p.exists():
            continue
        try:
            import pandas as pd

            df = pd.read_csv(p, parse_dates=["date"])
            return str(df.iloc[-1].get("regime", "unknown"))
        except Exception:
            pass
    return "unknown"


def _best_from_csv(path: Path, sort_col: str, name_col: str = "model_name", ascending: bool = False) -> str:
    if not path.exists():
        return "pending"
    try:
        import pandas as pd

        df = pd.read_csv(path)
        if df.empty or sort_col not in df.columns:
            return "pending"
        col = name_col if name_col in df.columns else df.columns[0]
        row = df.sort_values(sort_col, ascending=ascending).iloc[0]
        return f"{row[col]} ({sort_col}={row[sort_col]})"
    except Exception:
        return "pending"


def _rw_status() -> str:
    p = ROOT / "data/outputs/model_zoo_forecast_scorecard.csv"
    if not p.exists():
        return "pending"
    try:
        import pandas as pd

        df = pd.read_csv(p)
        beats = int(df["model_beats_rw_rmse"].sum()) if "model_beats_rw_rmse" in df.columns else 0
        return f"{beats} model(s) beat random walk by RMSE (mostly marginal)"
    except Exception:
        return "pending"


def _data_quality() -> str:
    p = ROOT / "data/outputs/data_quality_report.csv"
    if p.exists():
        return "see data_quality_report.csv in snapshot"
    return "Tier 4 prototype likely if FRED unavailable — verify data_quality layer"


def create_snapshot() -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    snap_dir = SNAPSHOTS / today
    snap_dir.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    copied += _copy_tree(ROOT / "data/outputs", snap_dir / "data/outputs")
    copied += _copy_tree(ROOT / "reports/publication", snap_dir / "reports/publication")

    for md in (ROOT / "reports").glob("*.md"):
        dst = snap_dir / "reports" / md.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(md, dst)
        copied.append(str(dst.relative_to(ROOT)))

    cfg_dst = snap_dir / "config.yaml"
    if (ROOT / "config.yaml").exists():
        shutil.copy2(ROOT / "config.yaml", cfg_dst)
        copied.append(str(cfg_dst.relative_to(ROOT)))

    summary_path = snap_dir / "SNAPSHOT_SUMMARY.md"
    commit = _git_hash()
    regime = _read_regime()
    best_strat = _best_from_csv(
        ROOT / "data/outputs/model_zoo_trading_scorecard.csv", "sharpe_net"
    )
    best_hedge = _best_from_csv(
        ROOT / "data/outputs/model_zoo_hedge_scorecard.csv",
        "cost_adjusted_risk_reduction",
    )
    if best_hedge == "pending":
        best_hedge = _best_from_csv(
            ROOT / "data/outputs/hedge_governance_scorecard.csv",
            "cost_adjusted_risk_reduction",
            name_col="policy_name",
        )

    summary = f"""# Research Snapshot Summary

**Snapshot date:** {today}  
**Git commit:** `{commit}`  
**Project:** Bowers Frontier Macro Labs — FX Lab

> Research and risk-framing only. Not investment advice. No live trading.

## Scripts typically run before snapshot

- `python scripts/run_usdmxn_backtest.py`
- `python scripts/run_under_tested_research.py`
- `python scripts/run_research_ladder.py --refresh`
- `python scripts/run_model_zoo.py`
- `python scripts/generate_model_zoo_report.py`
- `python scripts/build_site.py`

## Key output files copied

{chr(10).join(f'- `{c}`' for c in copied[:40])}
{"- ..." if len(copied) > 40 else ""}

**Total files copied:** {len(copied)}

## Latest state

| Item | Value |
|------|-------|
| USD/MXN regime | {regime} |
| Best trading model (Sharpe net) | {best_strat} |
| Best hedge policy (cost-adj risk reduction) | {best_hedge} |
| Random-walk forecast status | {_rw_status()} |
| Data quality | {_data_quality()} |

## Flagship thesis

A model may fail as a price forecast but still be useful for hedge governance.

## Disclaimer

Research and education only. Not investment advice. No guaranteed returns. No live trading.
"""
    summary_path.write_text(summary, encoding="utf-8")
    return snap_dir


def main() -> None:
    path = create_snapshot()
    print(f"Snapshot created: {path}")
    print(f"Summary: {path / 'SNAPSHOT_SUMMARY.md'}")


if __name__ == "__main__":
    main()
