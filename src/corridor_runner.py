"""
Multi-corridor FX research runner.

Research-only. One failed ticker must not crash the full roadmap.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from .backtest import scorecard, run_strategy_backtest
from .corridors import CORRIDOR_REGISTRY, get_corridor, list_corridors
from .data_loader import load_pair_prices
from .features import build_features
from .flow_pressure_tests import run_flow_pressure_tests
from .flow_proxies import add_corridor_flow_proxies
from .hedge_governance import GOVERNANCE_POLICIES, governance_metrics, run_hedge_governance_backtest
from .models import predict_regimes
from .random_walk_validity import build_random_walk_validity_map
from .regimes import classify_regimes

ROOT = Path(__file__).resolve().parents[1]


def _out_dirs(cfg: dict) -> Tuple[Path, Path]:
    proc = ROOT / "data" / "processed"
    out = ROOT / cfg.get("reporting", {}).get("output_dir", "data/outputs")
    if not out.is_absolute():
        out = ROOT / out
    proc.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    return proc, out


def _master_scorecard_rows(
    df: pd.DataFrame,
    cfg: dict,
    corridor_id: str,
    meta: dict,
    load_meta: Optional[dict] = None,
) -> List[dict]:
    from .data_provenance import build_run_provenance

    prov = build_run_provenance(
        cfg,
        df,
        currency_pair=meta.get("official_pair_label"),
        source=(load_meta or {}).get("source", "yfinance"),
        data_tier=(load_meta or {}).get("data_tier", "prototype"),
    )
    rows = []
    ann = int(cfg["backtest"]["annualization_days"])
    for mode in ["buy_and_hold", "legacy", "flat_range", "r2_only", "random_walk"]:
        bt = run_strategy_backtest(df, cfg, mode)
        n = len(bt)
        pos = bt["position"]
        rows.append(
            {
                "corridor_id": corridor_id,
                "model_pair": meta["model_pair"],
                "official_pair_label": meta["official_pair_label"],
                "mode": mode,
                "total_return": round(float((1 + bt["net_strategy_return"]).prod() - 1) * 100, 2),
                "annualized_return": round(
                    float(bt["net_strategy_return"].mean() * ann * 100), 2
                ),
                "annualized_volatility": round(
                    float(bt["net_strategy_return"].std() * (ann ** 0.5) * 100), 2
                ),
                "sharpe": round(
                    float(
                        bt["net_strategy_return"].mean()
                        / (bt["net_strategy_return"].std() + 1e-12)
                        * (ann ** 0.5)
                    ),
                    3,
                ),
                "max_drawdown": round(
                    float((bt["equity"] / bt["equity"].cummax() - 1).min() * 100), 2
                ),
                "number_of_trades": int(bt["turnover"].gt(0).sum()),
                "total_transaction_cost": round(float(bt["transaction_cost"].sum()) * 100, 3),
                "percent_time_in_market": round(float((pos != 0).mean()) * 100, 1),
                "observations": n,
                "start_date": str(df.index.min().date()) if n else None,
                "end_date": str(df.index.max().date()) if n else None,
                **{k: prov[k] for k in (
                    "source", "data_tier", "currency_pair", "sample_start", "sample_end",
                    "observations", "run_timestamp", "config_hash", "model_version",
                ) if k in prov},
            }
        )
    return rows


def run_single_corridor(
    corridor_id: str,
    cfg: dict,
    proc_dir: Path,
    out_dir: Path,
    save_individual: bool = True,
) -> Tuple[dict, Optional[pd.DataFrame]]:
    """Process one corridor; return download log row and master scorecard rows."""
    meta = get_corridor(corridor_id)
    ticker = meta["model_pair"]
    years = int(cfg["data"].get("history_years", 25))

    log = {
        "corridor_id": corridor_id,
        "model_pair": ticker,
        "official_pair_label": meta["official_pair_label"],
        "status": "failed",
        "error_message": "",
        "observations": 0,
        "start_date": None,
        "end_date": None,
        "data_source": "unknown",
        "data_tier": "prototype",
    }

    try:
        prices, load_meta = load_pair_prices(ticker, years)
        log["data_source"] = load_meta.get("source", "yfinance")
        log["data_tier"] = "prototype"

        feat = build_features(prices, cfg)
        feat["regime"] = predict_regimes(feat, cfg)
        feat = classify_regimes(feat, cfg)
        feat = add_corridor_flow_proxies(feat, corridor_id, meta)

        log["observations"] = len(feat)
        log["start_date"] = str(feat.index.min().date())
        log["end_date"] = str(feat.index.max().date())
        log["status"] = "success"

        if save_individual:
            feat_path = proc_dir / f"{corridor_id}_features_regimes.csv"
            flow_path = proc_dir / f"{corridor_id}_features_regimes_flow.csv"
            feat.to_csv(feat_path)
            feat.to_csv(flow_path)

            sc = scorecard(feat, cfg)
            sc.insert(0, "corridor_id", corridor_id)
            sc.to_csv(out_dir / f"{corridor_id}_scorecard.csv", index=False)

            rw = build_random_walk_validity_map(feat, corridor_id=corridor_id)
            rw.to_csv(out_dir / f"{corridor_id}_random_walk_validity_map.csv", index=False)

            fp = run_flow_pressure_tests(feat, corridor_id=corridor_id)
            fp.to_csv(out_dir / f"{corridor_id}_flow_pressure_test_results.csv", index=False)

            hg_rows = []
            hg_details = []
            for pol in GOVERNANCE_POLICIES:
                det = run_hedge_governance_backtest(
                    feat,
                    pol,
                    "receiver_currency_exposure",
                    cfg,
                    corridor_id=corridor_id,
                )
                hg_rows.append(governance_metrics(det))
                hg_details.append(det)
            hg_sc = pd.DataFrame(hg_rows)
            hg_sc.to_csv(out_dir / f"{corridor_id}_hedge_governance_scorecard.csv", index=False)
            pd.concat(hg_details).to_csv(
                out_dir / f"{corridor_id}_hedge_governance_detail.csv", index=False
            )

        master_rows = _master_scorecard_rows(feat, cfg, corridor_id, meta, load_meta)
        return log, pd.DataFrame(master_rows)

    except Exception as exc:
        log["error_message"] = str(exc)[:500]
        return log, None


def run_corridor_roadmap(cfg: dict) -> Dict[str, Path]:
    """Run priority corridors and write combined outputs."""
    proc_dir, out_dir = _out_dirs(cfg)
    c_cfg = cfg.get("corridors", {})
    priority = c_cfg.get("priority_to_run", 1)
    include_p2 = c_cfg.get("include_priority_2", False)
    save_ind = c_cfg.get("save_individual_outputs", True)

    corridors = list_corridors(priority=priority)
    if include_p2:
        corridors += list_corridors(priority=2)

    # De-duplicate by corridor_id (GULF_IN_PROXY shares USDINR with US_IN but is separate analysis)
    seen_ids = set()
    to_run = []
    for c in corridors:
        if c["corridor_id"] not in seen_ids:
            seen_ids.add(c["corridor_id"])
            to_run.append(c)

    logs: List[dict] = []
    master_frames: List[pd.DataFrame] = []
    rw_frames: List[pd.DataFrame] = []
    fp_frames: List[pd.DataFrame] = []
    hg_frames: List[pd.DataFrame] = []

    for c in to_run:
        cid = c["corridor_id"]
        print(f"  Corridor {cid} ({c['model_pair']})...")
        log, master = run_single_corridor(cid, cfg, proc_dir, out_dir, save_ind)
        logs.append(log)
        if master is not None:
            master_frames.append(master)
            rw_path = out_dir / f"{cid}_random_walk_validity_map.csv"
            fp_path = out_dir / f"{cid}_flow_pressure_test_results.csv"
            hg_path = out_dir / f"{cid}_hedge_governance_scorecard.csv"
            if rw_path.exists():
                rw_frames.append(pd.read_csv(rw_path))
            if fp_path.exists():
                fp_frames.append(pd.read_csv(fp_path))
            if hg_path.exists():
                hg_frames.append(pd.read_csv(hg_path))

    paths: Dict[str, Path] = {}
    paths["download_log"] = out_dir / "corridor_download_log.csv"
    pd.DataFrame(logs).to_csv(paths["download_log"], index=False)

    if master_frames:
        paths["master_scorecard"] = out_dir / "corridor_master_scorecard.csv"
        pd.concat(master_frames, ignore_index=True).to_csv(paths["master_scorecard"], index=False)

    if rw_frames:
        paths["random_walk_validity"] = out_dir / "corridor_random_walk_validity.csv"
        pd.concat(rw_frames, ignore_index=True).to_csv(paths["random_walk_validity"], index=False)

    if fp_frames:
        paths["flow_pressure"] = out_dir / "corridor_flow_pressure_summary.csv"
        pd.concat(fp_frames, ignore_index=True).to_csv(paths["flow_pressure"], index=False)

    if hg_frames:
        paths["hedge_governance"] = out_dir / "corridor_hedge_governance_summary.csv"
        pd.concat(hg_frames, ignore_index=True).to_csv(paths["hedge_governance"], index=False)

    return paths
