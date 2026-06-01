"""
Flagship research lane: Forecast Failure and Hedge Usefulness.

Separates forecast scorecard from hedge-governance OOS tests on USD/MXN.
Research-only — not investment advice.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from .carry_hedge_governance import run_carry_hedge_backtest
from .hedge_governance import (
    GOVERNANCE_POLICIES,
    governance_metrics,
    run_hedge_governance_backtest,
)
from .r1_r2_trend_quality import (
    build_r1_r2_trend_quality,
    build_r1_r2_trend_quality_oos,
    save_r1_r2_trend_quality,
)

ROOT = Path(__file__).resolve().parents[1]

STATIC_POLICIES = ["half_hedged", "mostly_hedged", "fully_hedged"]
DYNAMIC_POLICIES = [
    "regime_based",
    "r2_active_policy",
    "no_change_in_range",
    "volatility_triggered",
]
CARRY_POLICIES = [
    "static_50",
    "regime_only",
    "carry_adjusted_regime",
    "no_change_in_range_carry_aware",
]
FLAGSHIP_POLICIES = STATIC_POLICIES + DYNAMIC_POLICIES
COST_LAYERS = ["base", "forward_full"]

DEFAULT_EXPOSURE = "us_entity_long_mxn"


def _load_features() -> pd.DataFrame:
    for name in (
        "usdmxn_features_regimes_carry.csv",
        "usdmxn_features_regimes_news.csv",
        "usdmxn_features_regimes_flow.csv",
        "usdmxn_features_regimes.csv",
    ):
        path = ROOT / "data" / "processed" / name
        if path.exists():
            df = pd.read_csv(path, parse_dates=["date"])
            return df.set_index("date") if "date" in df.columns else df
    raise FileNotFoundError("Missing processed features. Run run_usdmxn_backtest.py first.")


def _slice(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    return df.loc[(df.index >= start) & (df.index <= end)].copy()


def _carry_data_ready(df: pd.DataFrame) -> bool:
    return "carry_fragility_regime" in df.columns and "is_high_carry" in df.columns


def _forward_points_loaded(df: pd.DataFrame) -> bool:
    if "forward_data_available" not in df.columns:
        return False
    return bool(df["forward_data_available"].fillna(False).any())


def _policy_class(policy_name: str) -> str:
    if policy_name in STATIC_POLICIES or policy_name == "static_50":
        return "static"
    if policy_name in CARRY_POLICIES:
        return "carry_aware"
    return "dynamic"


def _run_policy_oos(
    panel: pd.DataFrame,
    policy: str,
    cfg: dict,
    test_start: str,
    test_end: str,
    cost_layer: str,
    carry_mode: bool = False,
) -> Optional[dict]:
    try:
        if carry_mode:
            det = run_carry_hedge_backtest(
                panel, policy, DEFAULT_EXPOSURE, cfg, cost_layer=cost_layer
            )
        else:
            det = run_hedge_governance_backtest(
                panel,
                policy,
                DEFAULT_EXPOSURE,
                cfg,
                corridor_id="USDMXN=X",
                cost_layer=cost_layer,
            )
        det_test = det.loc[(det.index >= test_start) & (det.index <= test_end)]
        if len(det_test) < 20:
            return None
        m = governance_metrics(det_test)
        turnover = float(m.get("hedge_turnover", 0) or 0)
        cost_adj = float(m.get("cost_adjusted_risk_reduction", 0) or 0)
        if turnover < 0.001:
            efficiency = cost_adj
        else:
            efficiency = cost_adj / turnover
        m.update(
            {
                "policy_class": _policy_class(policy),
                "cost_layer": cost_layer,
                "turnover_efficiency": round(efficiency, 3),
                "status": "ok",
            }
        )
        return m
    except Exception as exc:
        return {
            "policy_name": policy,
            "policy_class": _policy_class(policy),
            "cost_layer": cost_layer,
            "status": "error",
            "error": str(exc)[:120],
        }


def run_flagship_hedge_oos(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """OOS hedge governance on pre-registered level-2 splits (base + forward_full costs)."""
    splits = cfg.get("research_ladder", {}).get("level2_splits", [])
    rows: list[dict] = []
    carry_ready = _carry_data_ready(df)

    for split in splits:
        name = split["name"]
        test_start = split["test_start"]
        test_end = split["test_end"]
        warmup_start = split.get("train_start", "2010-01-01")
        panel = _slice(df, warmup_start, test_end)
        if len(panel) < 40:
            continue

        policies: list[tuple[str, bool]] = [(p, False) for p in FLAGSHIP_POLICIES]
        if carry_ready:
            policies.extend((p, True) for p in CARRY_POLICIES)

        for cost_layer in COST_LAYERS:
            for policy, carry_mode in policies:
                if not carry_mode and policy not in GOVERNANCE_POLICIES:
                    continue
                result = _run_policy_oos(
                    panel, policy, cfg, test_start, test_end, cost_layer, carry_mode=carry_mode
                )
                if result is None:
                    continue
                result.update(
                    {
                        "split": name,
                        "test_period": f"{test_start}..{test_end}",
                        "test_bars": len(panel.loc[(panel.index >= test_start) & (panel.index <= test_end)]),
                    }
                )
                rows.append(result)

    return pd.DataFrame(rows)


def build_turnover_adjusted_comparison(oos: pd.DataFrame, cost_layer: str = "forward_full") -> pd.DataFrame:
    """
    Compare best dynamic/carry-aware policy vs best static benchmark per OOS split.

    Turnover efficiency = cost_adjusted_risk_reduction / max(turnover, 0.01).
    """
    if oos.empty or "status" not in oos.columns:
        return pd.DataFrame()

    ok = oos[(oos["status"] == "ok") & (oos.get("cost_layer", "base") == cost_layer)].copy()
    if ok.empty:
        return pd.DataFrame()

    rows: list[dict] = []
    for split in ok["split"].unique():
        sub = ok[ok["split"] == split]
        static = sub[sub["policy_class"] == "static"]
        dynamic = sub[sub["policy_class"].isin(["dynamic", "carry_aware"])]
        if static.empty or dynamic.empty:
            continue

        best_static = static.sort_values("cost_adjusted_risk_reduction", ascending=False).iloc[0]
        best_dynamic = dynamic.sort_values("turnover_efficiency", ascending=False).iloc[0]
        best_dynamic_car = dynamic.sort_values("cost_adjusted_risk_reduction", ascending=False).iloc[0]

        dyn_beats_static = float(best_dynamic["cost_adjusted_risk_reduction"]) >= float(
            best_static["cost_adjusted_risk_reduction"]
        )
        dyn_eff_beats = float(best_dynamic["turnover_efficiency"]) > float(best_static["turnover_efficiency"])

        rows.append(
            {
                "split": split,
                "test_period": best_static.get("test_period"),
                "cost_layer": cost_layer,
                "best_static_policy": best_static["policy_name"],
                "best_static_cost_adj": best_static["cost_adjusted_risk_reduction"],
                "best_static_turnover": best_static["hedge_turnover"],
                "best_static_efficiency": best_static["turnover_efficiency"],
                "best_dynamic_policy": best_dynamic["policy_name"],
                "best_dynamic_cost_adj": best_dynamic["cost_adjusted_risk_reduction"],
                "best_dynamic_turnover": best_dynamic["hedge_turnover"],
                "best_dynamic_efficiency": best_dynamic["turnover_efficiency"],
                "best_dynamic_by_cost_adj": best_dynamic_car["policy_name"],
                "dynamic_beats_static_cost_adj": dyn_beats_static,
                "dynamic_beats_static_efficiency": dyn_eff_beats,
            }
        )

    return pd.DataFrame(rows)


def _forecast_failure_summary() -> dict:
    path = ROOT / "data" / "outputs" / "model_zoo_forecast_scorecard.csv"
    if not path.exists():
        return {"available": False, "models_total": 0, "beats_rw_rmse": 0, "pct_beats_rw": None}

    fc = pd.read_csv(path)
    if fc.empty or "model_beats_rw_rmse" not in fc.columns:
        return {"available": False, "models_total": len(fc), "beats_rw_rmse": 0, "pct_beats_rw": None}

    total = len(fc)
    beats = int(fc["model_beats_rw_rmse"].sum())
    return {
        "available": True,
        "models_total": total,
        "beats_rw_rmse": beats,
        "pct_beats_rw": round(100.0 * beats / total, 1) if total else 0.0,
    }


def _best_dynamic_policy(oos: pd.DataFrame, cost_layer: str = "base") -> Optional[str]:
    ok = oos[(oos["status"] == "ok") & (oos.get("cost_layer", "base") == cost_layer)].copy()
    if ok.empty:
        return None
    dyn = ok[ok["policy_class"].isin(["dynamic", "carry_aware"])]
    if dyn.empty:
        return None
    idx = dyn["cost_adjusted_risk_reduction"].astype(float).idxmax()
    return str(dyn.loc[idx, "policy_name"])


def generate_flagship_report(
    cfg: dict,
    df: Optional[pd.DataFrame] = None,
    root: Optional[Path] = None,
) -> tuple[Path, pd.DataFrame, pd.DataFrame]:
    root = root or ROOT
    df = df if df is not None else _load_features()

    oos = run_flagship_hedge_oos(df, cfg)
    oos_path = root / "data" / "outputs" / "flagship_hedge_oos_scorecard.csv"
    oos_path.parent.mkdir(parents=True, exist_ok=True)
    oos.to_csv(oos_path, index=False)

    turnover_cmp = build_turnover_adjusted_comparison(oos, cost_layer="forward_full")
    turnover_path = root / "data" / "outputs" / "flagship_turnover_adjusted_comparison.csv"
    turnover_cmp.to_csv(turnover_path, index=False)

    splits = cfg.get("research_ladder", {}).get("level2_splits", [])
    r1r2 = build_r1_r2_trend_quality(df.reset_index(), corridor_id="USDMXN=X")
    save_r1_r2_trend_quality(r1r2)
    r1r2_oos = build_r1_r2_trend_quality_oos(df.reset_index(), splits, corridor_id="USDMXN=X")
    r1r2_oos_path = root / "data" / "outputs" / "r1_r2_trend_quality_oos.csv"
    r1r2_oos.to_csv(r1r2_oos_path, index=False)

    fc = _forecast_failure_summary()
    best_dyn_base = _best_dynamic_policy(oos, "base")
    best_dyn_ff = _best_dynamic_policy(oos, "forward_full")
    carry_ready = _carry_data_ready(df)
    forward_loaded = _forward_points_loaded(df)

    lines = [
        "# Flagship Research Lane — Forecast Failure and Hedge Usefulness",
        "",
        f"*Generated: {datetime.now():%Y-%m-%d %H:%M}*",
        "",
        "## Thesis",
        "",
        "Bowers Frontier Macro Labs does not need to prove that FX is predictable to create research value. "
        "The flagship lane tests whether regime intelligence improves hedge-governance decisions "
        "when price prediction fails.",
        "",
        "## Forecast Scorecard (separate object)",
        "",
    ]

    if fc["available"]:
        lines.extend(
            [
                f"- Models evaluated: **{fc['models_total']}**",
                f"- Beat random walk (RMSE): **{fc['beats_rw_rmse']}** ({fc['pct_beats_rw']}%)",
                "",
                "Interpretation: Most models still fail the forecast-accuracy benchmark. "
                "Hedge usefulness must be evaluated independently.",
                "",
            ]
        )
    else:
        lines.append("_Run model zoo first for forecast scorecard._\n")

    lines.extend(
        [
            "## Data Context",
            "",
            f"- Carry layer ready: **{carry_ready}** (policy-rate proxy; forward points required for true economics)",
            f"- Forward points CSV loaded: **{forward_loaded}**",
            "",
        ]
    )

    lines.extend(["## OOS Hedge Governance — base costs", ""])
    ok_base = oos[(oos["status"] == "ok") & (oos.get("cost_layer", "base") == "base")] if not oos.empty else oos
    _append_oos_section(lines, ok_base, best_dyn_base, "base")

    lines.extend(["## OOS Hedge Governance — forward_full costs", ""])
    ok_ff = oos[(oos["status"] == "ok") & (oos.get("cost_layer") == "forward_full")] if not oos.empty else oos
    _append_oos_section(lines, ok_ff, best_dyn_ff, "forward_full")

    lines.extend(["## Turnover-Adjusted Comparison (forward_full)", ""])
    if turnover_cmp.empty:
        lines.append("_Insufficient data for turnover-adjusted comparison._")
    else:
        for _, row in turnover_cmp.iterrows():
            lines.append(f"### {row['split']} ({row.get('test_period', '')})")
            lines.append(
                f"- Best static: `{row['best_static_policy']}` — cost-adj {row['best_static_cost_adj']}, "
                f"turnover {row['best_static_turnover']}, efficiency {row['best_static_efficiency']}"
            )
            lines.append(
                f"- Best dynamic (efficiency): `{row['best_dynamic_policy']}` — cost-adj {row['best_dynamic_cost_adj']}, "
                f"turnover {row['best_dynamic_turnover']}, efficiency {row['best_dynamic_efficiency']}"
            )
            lines.append(
                f"- Dynamic beats static on cost-adj: **{row['dynamic_beats_static_cost_adj']}** | "
                f"on turnover efficiency: **{row['dynamic_beats_static_efficiency']}**"
            )
            lines.append("")

    lines.extend(["## R1 vs R2 Trend Quality (full sample)", ""])
    if not r1r2.empty:
        for _, row in r1r2.iterrows():
            _append_r1r2_row(lines, row)

    lines.extend(["## R1 vs R2 Trend Quality (OOS test windows only)", ""])
    if r1r2_oos.empty:
        lines.append("_No OOS R1/R2 data._")
    else:
        for split in r1r2_oos["split"].unique():
            sub = r1r2_oos[r1r2_oos["split"] == split]
            lines.append(f"### {split}")
            for _, row in sub.iterrows():
                _append_r1r2_row(lines, row, indent="  ")
            if len(sub) == 2:
                r1 = sub[sub["regime"].str.contains("R1")]
                r2 = sub[sub["regime"].str.contains("R2")]
                if not r1.empty and not r2.empty:
                    cont_gap = (r2.iloc[0].get("continuation_probability") or 0) - (
                        r1.iloc[0].get("continuation_probability") or 0
                    )
                    lines.append(f"  - R2 minus R1 continuation: **{cont_gap:.4f}**")
            lines.append("")

    lines.extend(
        [
            "## Claim Discipline",
            "",
            "Results depend on data quality and cost assumptions. "
            "Static full hedge may dominate raw vol reduction; the research question is whether "
            "dynamic policies improve turnover-adjusted discipline when forecasts fail. "
            "This report does not claim trading readiness, FX predictability, or guaranteed hedge savings.",
            "",
        ]
    )

    report_path = root / "reports" / "FLAGSHIP_RESEARCH_LANE.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path, oos, r1r2


def _append_oos_section(lines: list[str], ok: pd.DataFrame, best_dyn: Optional[str], label: str) -> None:
    if ok.empty:
        lines.append(f"_Insufficient OOS hedge data ({label})._")
        return
    for split in ok["split"].unique():
        sub = ok[ok["split"] == split].sort_values("cost_adjusted_risk_reduction", ascending=False)
        lines.append(f"### {split} ({sub['test_period'].iloc[0]})")
        lines.append("")
        for _, row in sub.iterrows():
            pclass = row.get("policy_class", "—")
            lines.append(
                f"- **{row['policy_name']}** [{pclass}]: cost-adj {row.get('cost_adjusted_risk_reduction', '—')}, "
                f"turnover {row.get('hedge_turnover', '—')}, efficiency {row.get('turnover_efficiency', '—')}"
            )
        lines.append("")
    if best_dyn:
        lines.append(f"**Best dynamic/carry policy ({label}):** `{best_dyn}`")
        lines.append("")


def _append_r1r2_row(lines: list[str], row: pd.Series, indent: str = "") -> None:
    lines.append(f"{indent}### {row['regime']} ({row.get('sample', 'full')})")
    lines.append(f"{indent}- Continuation probability: {row.get('continuation_probability')}")
    lines.append(f"{indent}- Annualized vol: {row.get('annualized_volatility')}%")
    lines.append(f"{indent}- Max drawdown: {row.get('max_drawdown_pct')}%")
    lines.append(f"{indent}- Carry fragility rate: {row.get('carry_fragility_rate')}")
    lines.append(f"{indent}- Interpretation: {row.get('interpretation')}")
    lines.append("")
