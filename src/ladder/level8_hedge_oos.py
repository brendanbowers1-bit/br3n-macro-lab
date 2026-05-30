"""
Level 8 — Multi-pair out-of-sample hedge governance tests.

Pre-registered design: fixed OOS splits + optional walk-forward folds,
comparing no_change_in_range vs regime_based and static benchmarks.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from ..data_loader import load_pair_prices
from ..features import build_features
from ..hedge_governance import (
    GOVERNANCE_POLICIES,
    governance_metrics,
    run_hedge_governance_backtest,
)
from ..regimes import classify_regimes
from ..backtest import generate_walk_forward_folds

ROOT = Path(__file__).resolve().parents[2]

DEFAULT_HEDGE_OOS_POLICIES = [
    "half_hedged",
    "mostly_hedged",
    "regime_based",
    "no_change_in_range",
    "volatility_triggered",
]

DEFAULT_EXPOSURES = [
    "receiver_currency_exposure",
    "usd_liability_exposure",
]


def _slice(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    return df.loc[(df.index >= start) & (df.index <= end)].copy()


def exposures_for_pair(ticker: str, cfg: dict) -> List[str]:
    """Exposure types to test for a pair (pre-registration: >= 3 for USD/MXN)."""
    ho = cfg.get("hedge_oos", {})
    by_pair = ho.get("exposures_by_pair", {})
    if ticker in by_pair:
        return list(by_pair[ticker])
    if ticker == "USDMXN=X":
        return ["us_entity_long_mxn", "receiver_currency_exposure", "usd_liability_exposure"]
    return list(ho.get("exposures", DEFAULT_EXPOSURES))


def hedge_oos_policies(cfg: dict) -> List[str]:
    policies = cfg.get("hedge_oos", {}).get("policies", DEFAULT_HEDGE_OOS_POLICIES)
    return [p for p in policies if p in GOVERNANCE_POLICIES]


def _cost_layers(cfg: dict) -> List[str]:
    return list(cfg.get("hedge_oos", {}).get("cost_layers", ["base", "forward_full"]))


def _run_hedge_oos_cell(
    df: pd.DataFrame,
    policy_name: str,
    exposure_type: str,
    cfg: dict,
    eval_start: str,
    eval_end: str,
    warmup_start: str,
    ticker: str,
    split_name: str,
    oos_design: str,
    cost_layer: str = "base",
) -> dict:
    panel = _slice(df, warmup_start, eval_end)
    if len(panel) < 30:
        return {
            "status": "insufficient_data",
            "ticker": ticker,
            "policy_name": policy_name,
            "exposure_type": exposure_type,
            "split": split_name,
            "oos_design": oos_design,
            "cost_layer": cost_layer,
            "test_period": f"{eval_start}..{eval_end}",
            "sample": "test",
        }

    det = run_hedge_governance_backtest(
        panel, policy_name, exposure_type, cfg, corridor_id=ticker, cost_layer=cost_layer
    )
    det_eval = det.loc[(det.index >= eval_start) & (det.index <= eval_end)]
    if len(det_eval) < 20:
        return {
            "status": "insufficient_test_data",
            "ticker": ticker,
            "policy_name": policy_name,
            "exposure_type": exposure_type,
            "split": split_name,
            "oos_design": oos_design,
            "cost_layer": cost_layer,
            "test_period": f"{eval_start}..{eval_end}",
            "test_bars": len(det_eval),
            "sample": "test",
        }

    metrics = governance_metrics(det_eval)
    metrics.update(
        {
            "status": "ok",
            "ticker": ticker,
            "split": split_name,
            "oos_design": oos_design,
            "cost_layer": cost_layer,
            "test_period": f"{eval_start}..{eval_end}",
            "test_bars": len(det_eval),
            "sample": "test",
            "warmup_start": warmup_start,
        }
    )
    return metrics


def run_pair_fixed_split_hedge_oos(
    df: pd.DataFrame,
    cfg: dict,
    ticker: str,
) -> pd.DataFrame:
    """Apply Level 2 fixed splits to hedge policies on one pair."""
    splits = cfg.get("research_ladder", {}).get("level2_splits", [])
    policies = hedge_oos_policies(cfg)
    layers = _cost_layers(cfg)
    rows: List[dict] = []

    for sp in splits:
        for exposure in exposures_for_pair(ticker, cfg):
            for policy in policies:
                for cost_layer in layers:
                    rows.append(
                        _run_hedge_oos_cell(
                            df,
                            policy,
                            exposure,
                            cfg,
                            eval_start=sp["test_start"],
                            eval_end=sp["test_end"],
                            warmup_start=sp["train_start"],
                            ticker=ticker,
                            split_name=sp["name"],
                            oos_design="fixed_split",
                            cost_layer=cost_layer,
                        )
                    )
    return pd.DataFrame(rows)


def run_pair_walk_forward_hedge_oos(
    df: pd.DataFrame,
    cfg: dict,
    ticker: str,
) -> pd.DataFrame:
    """Rolling walk-forward OOS for hedge policies on one pair."""
    if not cfg.get("hedge_oos", {}).get("include_walk_forward", True):
        return pd.DataFrame()

    folds = generate_walk_forward_folds(df.index, cfg)
    policies = hedge_oos_policies(cfg)
    layers = _cost_layers(cfg)
    rows: List[dict] = []

    for fold in folds:
        split_name = f"wf_{fold.fold}"
        for exposure in exposures_for_pair(ticker, cfg):
            for policy in policies:
                for cost_layer in layers:
                    rows.append(
                        _run_hedge_oos_cell(
                            df,
                            policy,
                            exposure,
                            cfg,
                            eval_start=str(fold.test_start.date()),
                            eval_end=str(fold.test_end.date()),
                            warmup_start=str(fold.train_start.date()),
                            ticker=ticker,
                            split_name=split_name,
                            oos_design="walk_forward",
                            cost_layer=cost_layer,
                        )
                    )
    return pd.DataFrame(rows)


def load_pair_features(ticker: str, cfg: dict, force_refresh: bool = False) -> pd.DataFrame:
    years = int(cfg["data"]["history_years"])
    min_years = int(cfg.get("hedge_oos", {}).get("min_years_history", 15))
    px, _ = load_pair_prices(ticker, years, force_refresh=force_refresh)
    df = classify_regimes(build_features(px, cfg), cfg)
    span_years = (df.index.max() - df.index.min()).days / 365.25
    if span_years < min_years:
        raise ValueError(f"insufficient history ({span_years:.1f}y < {min_years}y)")
    return df


def run_multipair_hedge_oos(
    cfg: dict,
    tickers: Optional[List[str]] = None,
    force_refresh: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Run pre-registered multi-pair hedge OOS tests.

    Returns (scorecard, comparison, summary).
    """
    tickers = tickers or cfg.get("research_ladder", {}).get("pairs", [cfg["data"]["ticker"]])

    scorecard_frames: List[pd.DataFrame] = []
    errors: List[dict] = []

    for ticker in tickers:
        try:
            df = load_pair_features(ticker, cfg, force_refresh=force_refresh)
            fixed = run_pair_fixed_split_hedge_oos(df, cfg, ticker)
            wf = run_pair_walk_forward_hedge_oos(df, cfg, ticker)
            for part in (fixed, wf):
                if not part.empty:
                    scorecard_frames.append(part)
        except Exception as exc:
            errors.append({"ticker": ticker, "status": "error", "error": str(exc)[:200]})

    if errors:
        scorecard_frames.append(pd.DataFrame(errors))

    scorecard = pd.concat(scorecard_frames, ignore_index=True) if scorecard_frames else pd.DataFrame()
    comparison = compare_no_change_vs_regime(scorecard)
    static_cmp = compare_no_change_vs_static(scorecard)
    summary = aggregate_hedge_oos_summary(scorecard, comparison, static_cmp, cfg)
    return scorecard, comparison, summary, static_cmp


def _compare_two_policies(
    scorecard: pd.DataFrame,
    policy_a: str,
    policy_b: str,
    prefix_a: str,
    prefix_b: str,
) -> pd.DataFrame:
    if scorecard.empty:
        return pd.DataFrame()

    ok = scorecard[scorecard["status"] == "ok"] if "status" in scorecard.columns else scorecard
    if ok.empty:
        return pd.DataFrame()

    keys = ["ticker", "split", "exposure_type", "oos_design", "test_period", "cost_layer"]
    a = ok[ok["policy_name"] == policy_a].set_index(keys)
    b = ok[ok["policy_name"] == policy_b].set_index(keys)
    shared = a.index.intersection(b.index)
    if len(shared) == 0:
        return pd.DataFrame()

    rows: List[dict] = []
    for idx in shared:
        a_row = a.loc[idx]
        b_row = b.loc[idx]
        if isinstance(a_row, pd.DataFrame):
            a_row = a_row.iloc[0]
        if isinstance(b_row, pd.DataFrame):
            b_row = b_row.iloc[0]

        a_turn = float(a_row["hedge_turnover"])
        b_turn = float(b_row["hedge_turnover"])
        rows.append(
            {
                "ticker": idx[0],
                "split": idx[1],
                "exposure_type": idx[2],
                "oos_design": idx[3],
                "test_period": idx[4],
                "cost_layer": idx[5],
                f"{prefix_a}_cost_adj": a_row["cost_adjusted_risk_reduction"],
                f"{prefix_b}_cost_adj": b_row["cost_adjusted_risk_reduction"],
                f"{prefix_a}_turnover": a_turn,
                f"{prefix_b}_turnover": b_turn,
                f"{prefix_a}_wins_cost_adj": float(a_row["cost_adjusted_risk_reduction"])
                > float(b_row["cost_adjusted_risk_reduction"]),
                "turnover_reduction_pct": round((1.0 - a_turn / b_turn) * 100, 2) if b_turn > 0 else None,
            }
        )
    return pd.DataFrame(rows)


def compare_no_change_vs_regime(scorecard: pd.DataFrame) -> pd.DataFrame:
    """Pairwise OOS comparison: no_change_in_range vs regime_based."""
    cmp_df = _compare_two_policies(
        scorecard,
        "no_change_in_range",
        "regime_based",
        "no_change",
        "regime_based",
    )
    if cmp_df.empty:
        return cmp_df
    cmp_df = cmp_df.rename(
        columns={
            "no_change_cost_adj": "no_change_cost_adj_risk_reduction",
            "regime_based_cost_adj": "regime_based_cost_adj_risk_reduction",
            "no_change_turnover": "no_change_turnover",
            "regime_based_turnover": "regime_based_turnover",
            "no_change_wins_cost_adj": "no_change_wins_cost_adj",
        }
    )
    cmp_df["no_change_wins_turnover"] = cmp_df["no_change_turnover"] < cmp_df["regime_based_turnover"]
    return cmp_df


def compare_no_change_vs_static(scorecard: pd.DataFrame) -> pd.DataFrame:
    """H8d: no_change vs static 50% and 75% under forward_full costs."""
    half = _compare_two_policies(scorecard, "no_change_in_range", "half_hedged", "no_change", "half")
    mostly = _compare_two_policies(scorecard, "no_change_in_range", "mostly_hedged", "no_change", "mostly")
    frames = []
    if not half.empty:
        half = half.assign(static_benchmark="half_hedged")
        frames.append(half)
    if not mostly.empty:
        mostly = mostly.assign(static_benchmark="mostly_hedged")
        frames.append(mostly)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _layer_summary(
    comparison: pd.DataFrame,
    static_cmp: pd.DataFrame,
    cost_layer: str,
    pairs_tested: int,
    exposures_tested: int,
    cfg: dict,
) -> dict:
    cmp_layer = comparison[comparison["cost_layer"] == cost_layer] if "cost_layer" in comparison.columns else comparison
    static_layer = (
        static_cmp[static_cmp["cost_layer"] == cost_layer] if "cost_layer" in static_cmp.columns else static_cmp
    )

    h8a_pass = h8b_pass = h8d_pass = False
    pct_pairs_h8a = median_turnover_red = pct_pairs_h8d = None
    pairs_no_change_wins = 0

    if not cmp_layer.empty:
        by_pair = cmp_layer.groupby("ticker")["no_change_wins_cost_adj"].agg(["mean", "count"])
        pairs_no_change_wins = int((by_pair["mean"] >= 0.5).sum())
        pct_pairs_h8a = round(100.0 * pairs_no_change_wins / len(by_pair), 2) if len(by_pair) else 0.0
        h8a_pass = pct_pairs_h8a >= 50.0
        valid_turn = cmp_layer["turnover_reduction_pct"].dropna()
        if not valid_turn.empty:
            median_turnover_red = round(float(valid_turn.median()), 2)
            h8b_pass = median_turnover_red >= 40.0

    if not static_layer.empty and "no_change_wins_cost_adj" in static_layer.columns:
        by_pair_static = static_layer.groupby("ticker")["no_change_wins_cost_adj"].mean()
        pairs_h8d = int((by_pair_static >= 0.5).sum())
        pct_pairs_h8d = round(100.0 * pairs_h8d / len(by_pair_static), 2)
        h8d_pass = pct_pairs_h8d >= 50.0

    min_pairs = int(cfg.get("hedge_oos", {}).get("min_pairs", 10))
    return {
        "cost_layer": cost_layer,
        "pairs_tested": pairs_tested,
        "min_pairs_target": min_pairs,
        "exposure_types_tested": exposures_tested,
        "comparison_cells": len(cmp_layer),
        "pairs_no_change_wins_h8a": pairs_no_change_wins,
        "pct_pairs_h8a": pct_pairs_h8a,
        "h8a_pass": h8a_pass,
        "median_turnover_reduction_pct": median_turnover_red,
        "h8b_pass": h8b_pass,
        "pct_pairs_h8d": pct_pairs_h8d,
        "h8d_pass": h8d_pass,
        "exposures_pass": exposures_tested >= 3,
        "pairs_panel_pass": pairs_tested >= min_pairs,
    }


def aggregate_hedge_oos_summary(
    scorecard: pd.DataFrame,
    comparison: pd.DataFrame,
    static_cmp: pd.DataFrame,
    cfg: dict,
) -> pd.DataFrame:
    """Panel summary vs pre-registered H8a / H8b / H8d thresholds, by cost layer."""
    ok = scorecard[scorecard["status"] == "ok"] if "status" in scorecard.columns else scorecard
    pairs_tested = int(ok["ticker"].nunique()) if not ok.empty and "ticker" in ok.columns else 0
    exposures_tested = int(ok["exposure_type"].nunique()) if not ok.empty and "exposure_type" in ok.columns else 0

    rows = []
    for layer in _cost_layers(cfg):
        layer_ok = ok[ok["cost_layer"] == layer] if "cost_layer" in ok.columns else ok
        pt = int(layer_ok["ticker"].nunique()) if not layer_ok.empty else pairs_tested
        et = int(layer_ok["exposure_type"].nunique()) if not layer_ok.empty else exposures_tested
        rows.append(_layer_summary(comparison, static_cmp, layer, pt, et, cfg))

    return pd.DataFrame(rows)


def save_hedge_oos_outputs(
    scorecard: pd.DataFrame,
    comparison: pd.DataFrame,
    summary: pd.DataFrame,
    out_dir: Optional[Path] = None,
    static_cmp: Optional[pd.DataFrame] = None,
) -> Dict[str, Path]:
    out_dir = out_dir or ROOT / "reports" / "research_ladder"
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "scorecard": out_dir / "level8_hedge_oos_scorecard.csv",
        "comparison": out_dir / "level8_hedge_oos_comparison.csv",
        "summary": out_dir / "level8_hedge_oos_summary.csv",
    }
    scorecard.to_csv(paths["scorecard"], index=False)
    comparison.to_csv(paths["comparison"], index=False)
    summary.to_csv(paths["summary"], index=False)
    if static_cmp is not None and not static_cmp.empty:
        static_path = out_dir / "level8_hedge_oos_static_comparison.csv"
        static_cmp.to_csv(static_path, index=False)
        paths["static_comparison"] = static_path
    return paths


def hedge_oos_report_md(scorecard: pd.DataFrame, comparison: pd.DataFrame, summary: pd.DataFrame) -> str:
    """Markdown section for research ladder."""
    if summary.empty:
        return "_Multi-pair hedge OOS not run. Execute `python scripts/run_multipair_hedge_oos.py`._\n"

    lines = ["### Multi-pair hedge OOS summary (pre-registered)", ""]

    for _, s in summary.iterrows():
        layer = s.get("cost_layer", "base")
        lines.extend(
            [
                f"**Cost layer: `{layer}`**",
                "",
                f"- Pairs tested: **{s.get('pairs_tested', '—')}** (target ≥ {s.get('min_pairs_target', 10)})",
                f"- Exposure types: **{s.get('exposure_types_tested', '—')}**",
                f"- H8a (no_change vs regime_based): **{'PASS' if s.get('h8a_pass') else 'FAIL'}** "
                f"({s.get('pct_pairs_h8a', '—')}% of pairs)",
                f"- H8b (median turnover reduction): **{'PASS' if s.get('h8b_pass') else 'FAIL'}** "
                f"({s.get('median_turnover_reduction_pct', '—')}%)",
                f"- H8d (no_change vs static 50%/75%): **{'PASS' if s.get('h8d_pass') else 'FAIL'}** "
                f"({s.get('pct_pairs_h8d', '—')}% of pairs)",
                "",
            ]
        )

    lines.append(
        "**Note:** `forward_full` adds spread/slippage + forward roll + carry drag from per-pair "
        "economic assumptions — still not a live forward curve. Level 8 gate requires all nine "
        "requirements **Met**."
    )
    lines.append("")

    ff = comparison[comparison["cost_layer"] == "forward_full"] if "cost_layer" in comparison.columns else comparison
    if not ff.empty:
        by_pair = (
            ff.groupby("ticker")
            .agg(
                cells=("no_change_wins_cost_adj", "count"),
                win_rate=("no_change_wins_cost_adj", "mean"),
                median_turnover_red=("turnover_reduction_pct", "median"),
            )
            .reset_index()
        )
        lines.append("### Per-pair OOS — forward_full (no_change vs regime_based)")
        lines.append("")
        lines.append("| ticker | cells | win_rate | median_turnover_red_% |")
        lines.append("| --- | --- | --- | --- |")
        for _, row in by_pair.sort_values("ticker").iterrows():
            wr = f"{100 * row['win_rate']:.1f}" if pd.notna(row["win_rate"]) else "—"
            tr = f"{row['median_turnover_red']:.1f}" if pd.notna(row["median_turnover_red"]) else "—"
            lines.append(f"| {row['ticker']} | {int(row['cells'])} | {wr} | {tr} |")
        lines.append("")

    err = scorecard[scorecard.get("status", "ok") == "error"] if "status" in scorecard.columns else pd.DataFrame()
    if not err.empty:
        lines.append(f"_Pair errors: {len(err)} — see scorecard `status` column._")
        lines.append("")

    return "\n".join(lines)
