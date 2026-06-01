#!/usr/bin/env python3
"""
Run FX desk decision framework — scorecards and corridor memos.

Research and risk-framing only. Not investment advice.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data" / "outputs"
PROC = ROOT / "data" / "processed"
MEMO_DIR = ROOT / "reports" / "fx_desk_memos"

from src.corridors import get_corridor, list_corridors
from src.fx_desk_memo import generate_fx_desk_memo
from src.fx_desk_scorecard import build_fx_desk_scorecard


def _read_csv(path: Path) -> Optional[pd.DataFrame]:
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            return None
    return None


def _load_features(corridor_id: str) -> Optional[pd.DataFrame]:
    for name in (f"{corridor_id}_features_regimes_flow.csv", f"{corridor_id}_features_regimes.csv"):
        p = PROC / name
        if p.exists():
            df = pd.read_csv(p, parse_dates=["date"] if "date" in pd.read_csv(p, nrows=0).columns else None)
            if "date" in df.columns:
                df = df.set_index("date")
            return df.sort_index()
    if corridor_id == "US_MX":
        for name in ("usdmxn_features_regimes_flow.csv", "usdmxn_features_regimes.csv"):
            p = PROC / name
            if p.exists():
                df = pd.read_csv(p, parse_dates=["date"] if "date" in pd.read_csv(p, nrows=0).columns else None)
                if "date" in df.columns:
                    df = df.set_index("date")
                return df.sort_index()
    return None


def _random_walk_status() -> str:
    fc = _read_csv(OUT / "forecast_scorecard.csv")
    if fc is not None and not fc.empty:
        if bool(fc.iloc[0].get("model_beats_rw_rmse", False)):
            return "Weak evidence"
    ac = _read_csv(OUT / "academic_test_results.csv")
    if ac is not None:
        dm = ac[ac["test"] == "diebold_mariano_rmse"]
        if not dm.empty:
            p = dm.iloc[0].get("p_value")
            if p is not None and float(p) < 0.05:
                return "Potential structure"
    return "Not beaten"


def _data_quality_flag() -> Optional[str]:
    dq = _read_csv(OUT / "data_quality_report.csv")
    if dq is not None and not dq.empty:
        return str(dq.iloc[0].get("data_quality_flag", "OK"))
    return "OK"


def _best_hedge_policy() -> Optional[str]:
    hg = _read_csv(OUT / "hedge_governance_scorecard.csv")
    if hg is None or hg.empty:
        return None
    us = hg[hg["exposure_type"] == "us_entity_long_mxn"] if "exposure_type" in hg.columns else hg
    dyn = us[~us["policy_name"].isin(["fully_hedged", "never_hedged"])] if not us.empty else us
    if dyn.empty:
        return None
    return str(dyn.loc[dyn["cost_adjusted_risk_reduction"].astype(float).idxmax(), "policy_name"])


def _flow_window_active(corridor_id: str) -> bool:
    fp_path = OUT / f"{corridor_id}_flow_pressure_test_results.csv"
    fp = _read_csv(fp_path)
    if fp is None:
        fp = _read_csv(OUT / "flow_pressure_test_results.csv")
    if fp is not None and corridor_id != "US_MX" and "corridor_id" in fp.columns:
        sub = fp[fp["corridor_id"] == corridor_id]
        if not sub.empty:
            fp = sub
    df = _load_features(corridor_id)
    if df is not None and "is_flow_pressure_window" in df.columns:
        return bool(df["is_flow_pressure_window"].iloc[-1])
    return False


def _volatility_state(df: Optional[pd.DataFrame]) -> str:
    if df is None or df.empty:
        return "Unknown"
    if "high_vol_flag" in df.columns:
        return "High volatility" if bool(df["high_vol_flag"].iloc[-1]) else "Low volatility"
    if "realized_vol" in df.columns:
        vol = float(df["realized_vol"].iloc[-1])
        return "High volatility" if vol > df["realized_vol"].median() else "Low volatility"
    return "Unknown"


def build_corridor_scorecard(corridor_id: str) -> Dict[str, Any]:
    """Assemble scorecard inputs for one corridor from lab outputs."""
    try:
        meta = get_corridor(corridor_id)
        pair_label = meta["official_pair_label"]
    except KeyError:
        pair_label = corridor_id

    df = _load_features(corridor_id)
    latest_regime = str(df["regime"].iloc[-1]) if df is not None and "regime" in df.columns else None

    return build_fx_desk_scorecard(
        corridor_id=corridor_id,
        pair_label=pair_label,
        latest_regime=latest_regime,
        volatility_state=_volatility_state(df),
        flow_window=_flow_window_active(corridor_id),
        data_quality_flag=_data_quality_flag(),
        hedge_policy_result=_best_hedge_policy(),
        random_walk_status=_random_walk_status(),
    )


def run_fx_desk_framework() -> Path:
    """Build scorecards and memos for USD/MXN and corridor roadmap if available."""
    OUT.mkdir(parents=True, exist_ok=True)
    MEMO_DIR.mkdir(parents=True, exist_ok=True)

    corridors: List[str] = ["US_MX"]
    dl = _read_csv(OUT / "corridor_download_log.csv")
    if dl is not None and "corridor_id" in dl.columns:
        ok = dl[dl["status"] == "success"]["corridor_id"].tolist()
        for cid in ok:
            if cid not in corridors:
                corridors.append(cid)

    rows: List[Dict[str, Any]] = []
    for cid in corridors:
        sc = build_corridor_scorecard(cid)
        rows.append(sc)
        memo_path = MEMO_DIR / f"{cid}_fx_desk_memo.md"
        generate_fx_desk_memo(sc, memo_path)

    scorecard_path = OUT / "fx_desk_scorecard.csv"
    pd.DataFrame(rows).to_csv(scorecard_path, index=False)
    return scorecard_path


def main() -> None:
    print("\nBowers Frontier Macro Labs — FX Desk Decision Framework")
    print("=" * 55)

    path = run_fx_desk_framework()
    df = pd.read_csv(path)

    print(f"\nSaved: {path}")
    print(f"Memos: {MEMO_DIR}/")
    print("\nSummary:")
    for _, row in df.iterrows():
        print(f"\n  Corridor: {row['corridor_id']} ({row['pair_label']})")
        print(f"  Latest regime: {row['latest_regime']}")
        print(f"  Overall desk risk: {row['overall_desk_risk_level']}")
        print(f"  Hedge timing: {row['hedge_timing_posture'][:70]}...")
        print(f"  Prefunding: {row['prefunding_posture'][:70]}...")
        print(f"  Pricing: {row['customer_pricing_posture'][:70]}...")
        if row.get("data_quality_warning"):
            print(f"  Data quality: {row['data_quality_warning'][:70]}...")

    print("\nResearch and risk-framing only. Not investment advice.")
    print("=" * 55)


if __name__ == "__main__":
    main()
