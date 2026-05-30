"""
Corridor roadmap report generator.

Reads multi-corridor outputs and writes reports/corridor_roadmap_report.md.
Exploratory research only — public calendar proxies are not payment-flow data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from .corridors import corridor_summary_dataframe, get_corridor, list_corridors

ROOT = Path(__file__).resolve().parents[1]


def _df_to_md_table(df: pd.DataFrame) -> str:
    """Simple markdown table without tabulate dependency."""
    if df.empty:
        return "_No data._"
    cols = list(df.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |"]
    lines.append("| " + " | ".join("---" for _ in cols) + " |")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def _read_csv(root: Path, rel: str) -> Optional[pd.DataFrame]:
    p = root / rel
    if p.exists():
        return pd.read_csv(p)
    return None


def _best_strategy(master: pd.DataFrame) -> pd.DataFrame:
    """Best Sharpe and lowest max drawdown per corridor (exclude buy_and_hold/random_walk)."""
    if master.empty:
        return pd.DataFrame()
    trade_modes = master[~master["mode"].isin(["buy_and_hold", "random_walk"])]
    if trade_modes.empty:
        trade_modes = master
    rows = []
    for cid, grp in trade_modes.groupby("corridor_id"):
        best_sh = grp.loc[grp["sharpe"].astype(float).idxmax()]
        best_dd = grp.loc[grp["max_drawdown"].astype(float).idxmax()]  # max_drawdown is negative; idxmax = least bad
        rows.append(
            {
                "corridor_id": cid,
                "best_sharpe_mode": best_sh["mode"],
                "best_sharpe": best_sh["sharpe"],
                "best_drawdown_mode": best_dd["mode"],
                "max_drawdown": best_dd["max_drawdown"],
            }
        )
    return pd.DataFrame(rows)


def _strongest_corridors(
    dl: pd.DataFrame,
    master: pd.DataFrame,
    rw: pd.DataFrame,
    hg: pd.DataFrame,
) -> list[str]:
    """Heuristic ranking for further research."""
    scores: dict[str, float] = {}
    for c in list_corridors():
        cid = c["corridor_id"]
        score = 0.0
        if not dl.empty:
            row = dl[dl["corridor_id"] == cid]
            if not row.empty and row.iloc[0]["status"] == "success":
                obs = int(row.iloc[0].get("observations", 0) or 0)
                if obs >= 3000:
                    score += 2
                elif obs >= 1500:
                    score += 1
        if not rw.empty:
            sub = rw[(rw["corridor_id"] == cid) if "corridor_id" in rw.columns else rw["regime"].notna()]
            if "corridor_id" in rw.columns:
                sub = rw[rw["corridor_id"] == cid]
            if not sub.empty:
                struct = (sub["random_walk_validity_label"] == "Potential structure").sum()
                score += min(struct, 2) * 0.5
        if not hg.empty and "corridor_id" in hg.columns:
            sub = hg[hg["corridor_id"] == cid]
            if not sub.empty and "cost_adjusted_risk_reduction" in sub.columns:
                best = sub["cost_adjusted_risk_reduction"].astype(float).max()
                if best > 0:
                    score += 1
        if c.get("data_warning"):
            score -= 0.5
        scores[cid] = score
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [k for k, v in ranked if v >= 1.5][:5]


def _weakest_corridors(dl: pd.DataFrame) -> list[str]:
    weak = []
    if dl.empty:
        return weak
    for _, row in dl.iterrows():
        cid = row["corridor_id"]
        if row.get("status") != "success":
            weak.append(f"{cid} (download failed: {row.get('error_message', '')[:80]})")
            continue
        obs = int(row.get("observations", 0) or 0)
        if obs < 500:
            weak.append(f"{cid} (limited observations: {obs})")
        try:
            meta = get_corridor(cid)
            if meta.get("data_warning"):
                weak.append(f"{cid} — {meta['data_warning']}")
        except KeyError:
            pass
    return weak


def generate_corridor_roadmap_report(root: Optional[Path] = None) -> Path:
    """Build markdown corridor roadmap report from available outputs."""
    root = root or ROOT
    out_dir = root / "data" / "outputs"
    report_dir = root / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "corridor_roadmap_report.md"

    registry = corridor_summary_dataframe()
    dl = _read_csv(root, "data/outputs/corridor_download_log.csv")
    master = _read_csv(root, "data/outputs/corridor_master_scorecard.csv")
    rw = _read_csv(root, "data/outputs/corridor_random_walk_validity.csv")
    fp = _read_csv(root, "data/outputs/corridor_flow_pressure_summary.csv")
    hg = _read_csv(root, "data/outputs/corridor_hedge_governance_summary.csv")

    lines: list[str] = []
    lines.append("# Remittance Corridor Roadmap Report")
    lines.append("")
    lines.append("*BR3N Macro Labs — research only, not investment advice.*")
    lines.append("")

    # 1. Purpose
    lines.append("## 1. Purpose")
    lines.append("")
    lines.append(
        "The corridor roadmap expands BR3N Macro Labs from USD/MXN into major remittance "
        "and payment corridors. This is exploratory research that separates **forecast accuracy**, "
        "**trading P&L**, and **hedge-governance usefulness**. Public calendar proxies are "
        "**not** actual order-flow or payment-flow data."
    )
    lines.append("")

    # 2. Corridor roadmap
    lines.append("## 2. Corridor roadmap")
    lines.append("")
    if not registry.empty:
        lines.append(_df_to_md_table(registry))
    else:
        lines.append("_No corridor registry data._")
    lines.append("")

    # 3. Data availability
    lines.append("## 3. Data availability summary")
    lines.append("")
    if dl is not None and not dl.empty:
        lines.append(_df_to_md_table(dl))
        ok = dl[dl["status"] == "success"]["corridor_id"].tolist()
        fail = dl[dl["status"] != "success"]["corridor_id"].tolist()
        lines.append("")
        lines.append(f"- **Succeeded:** {', '.join(ok) or 'none'}")
        lines.append(f"- **Failed:** {', '.join(fail) or 'none'}")
    else:
        lines.append("_Run `python scripts/run_corridor_roadmap.py` first._")
    lines.append("")

    # 4. Strategy comparison
    lines.append("## 4. Strategy comparison by corridor")
    lines.append("")
    if master is not None and not master.empty:
        best = _best_strategy(master)
        if not best.empty:
            lines.append(_df_to_md_table(best))
        lines.append("")
        lines.append("Full scorecard (selected columns):")
        cols = [
            c
            for c in [
                "corridor_id",
                "mode",
                "sharpe",
                "max_drawdown",
                "total_return",
                "number_of_trades",
            ]
            if c in master.columns
        ]
        lines.append(_df_to_md_table(master[cols]))
    else:
        lines.append("_No corridor master scorecard._")
    lines.append("")

    # 5. Random-walk validity
    lines.append("## 5. Random-walk validity by corridor")
    lines.append("")
    if rw is not None and not rw.empty:
        show = rw[
            [
                c
                for c in [
                    "corridor_id",
                    "regime",
                    "random_walk_validity_label",
                    "annualized_volatility",
                    "autocorrelation_1d",
                    "interpretation",
                ]
                if c in rw.columns
            ]
        ]
        lines.append(_df_to_md_table(show))
    else:
        lines.append("_No random-walk validity map._")
    lines.append("")

    # 6. Flow pressure
    lines.append("## 6. Flow-pressure window results")
    lines.append("")
    lines.append(
        "_Exploratory only — calendar proxies are not causal payment-flow data._"
    )
    lines.append("")
    if fp is not None and not fp.empty:
        show = fp[
            [
                c
                for c in [
                    "corridor_id",
                    "observations_flow_window",
                    "observations_normal",
                    "volatility_flow_window",
                    "volatility_normal",
                    "p_value_return_difference",
                    "interpretation",
                ]
                if c in fp.columns
            ]
        ]
        lines.append(_df_to_md_table(show))
    else:
        lines.append("_No flow-pressure summary._")
    lines.append("")

    # 7. Hedge governance
    lines.append("## 7. Hedge-governance results")
    lines.append("")
    lines.append(
        "_Simplified hedge-governance research — not ASC 815 / IFRS 9 hedge accounting._"
    )
    lines.append("")
    if hg is not None and not hg.empty:
        best_rows = []
        for cid, grp in hg.groupby("corridor_id"):
            idx = grp["cost_adjusted_risk_reduction"].astype(float).idxmax()
            best_rows.append(grp.loc[idx])
        best_hg = pd.DataFrame(best_rows)
        show = best_hg[
            [
                c
                for c in [
                    "corridor_id",
                    "policy_name",
                    "cost_adjusted_risk_reduction",
                    "hedge_turnover",
                    "total_hedge_cost",
                    "average_hedge_ratio",
                ]
                if c in best_hg.columns
            ]
        ]
        lines.append("Best policy by cost-adjusted risk reduction:")
        lines.append("")
        lines.append(_df_to_md_table(show))
    else:
        lines.append("_No hedge-governance summary._")
    lines.append("")

    # 8. Strongest corridors
    lines.append("## 8. Strongest corridors for further research")
    lines.append("")
    if dl is not None:
        strong = _strongest_corridors(
            dl if dl is not None else pd.DataFrame(),
            master if master is not None else pd.DataFrame(),
            rw if rw is not None else pd.DataFrame(),
            hg if hg is not None else pd.DataFrame(),
        )
        if strong:
            for cid in strong:
                try:
                    meta = get_corridor(cid)
                    lines.append(
                        f"- **{cid}** ({meta['official_pair_label']}): "
                        f"{meta['corridor_theme']}"
                    )
                except KeyError:
                    lines.append(f"- **{cid}**")
        else:
            lines.append("_Insufficient combined evidence yet — rerun after data upgrades._")
    else:
        lines.append("_Run corridor roadmap first._")
    lines.append("")

    # 9. Weakest / unreliable
    lines.append("## 9. Weakest / unreliable data corridors")
    lines.append("")
    weak = _weakest_corridors(dl if dl is not None else pd.DataFrame())
    if weak:
        for w in weak:
            lines.append(f"- {w}")
    else:
        lines.append("_No major data failures flagged._")
    lines.append("")

    # 10. Next data upgrades
    lines.append("## 10. Next data upgrades")
    lines.append("")
    upgrades = [
        "Federal Reserve H.10 / FRED spot series where available (USD/MXN, USD/INR, etc.)",
        "BIS effective exchange rates for cross-checks",
        "World Bank remittance inflows by corridor",
        "Central bank remittance and spot data (Banxico, RBI, BSP, Banrep, BCB)",
        "Professional forward/FX data (Bloomberg, LSEG, FactSet) for bid/ask and forward points",
        "Legally usable proprietary payment-flow data only with proper authorization",
    ]
    for u in upgrades:
        lines.append(f"- {u}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("**Disclaimer:** This is exploratory research. Public calendar proxies are not "
                  "actual order-flow or payment-flow data. Results should be treated as hypotheses "
                  "until validated with academic-grade data and, where legally available, "
                  "proprietary payment-flow data.")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
