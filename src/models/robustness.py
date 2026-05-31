"""
Robustness checks for VSI corridor rankings and loss estimates.

Research-only. Results are robust if corridor rankings remain similar across specifications.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.indices.value_survival import calculate_vsi_for_corridors


def _corridor_rank(df: pd.DataFrame, col: str = "value_survival_index") -> pd.Series:
    agg = df.groupby("corridor", as_index=False)[col].mean()
    agg = agg.sort_values(col)
    agg["rank"] = range(1, len(agg) + 1)
    return agg.set_index("corridor")["rank"]


def _rank_correlation(r1: pd.Series, r2: pd.Series) -> float:
    common = r1.index.intersection(r2.index)
    if len(common) < 3:
        return float("nan")
    a = r1.reindex(common).astype(float)
    b = r2.reindex(common).astype(float)
    return float(a.corr(b, method="spearman"))


def run_robustness_checks(
    corridor_prices: pd.DataFrame,
    fx_rates: pd.DataFrame | None = None,
    macro: pd.DataFrame | None = None,
    trust_scores: pd.DataFrame | None = None,
    dollar_dependency: pd.DataFrame | None = None,
    mock_data_flag: bool = False,
) -> pd.DataFrame:
    """Run specification variants and return comparison table."""
    baseline = calculate_vsi_for_corridors(
        corridor_prices, fx_rates, macro, trust_scores, dollar_dependency,
        mock_data_flag=mock_data_flag, sensitivity_case="baseline",
    )
    base_rank = _corridor_rank(baseline, "vsi_risk_adjusted")

    checks: list[dict] = []

    # 1. Core only (exclude extended components)
    core_only = baseline.copy()
    core_only["value_survival_index"] = core_only["vsi_core"]
    core_only["total_value_loss_pct"] = core_only["vsi_core_loss_pct"]
    r = _corridor_rank(core_only, "value_survival_index")
    checks.append(_check_row("exclude_trust_and_dollar", base_rank, r, baseline, core_only))

    # 2. Exclude volatility penalty
    no_vol = baseline.copy()
    no_vol["value_survival_index"] = no_vol["vsi_core"]
    no_vol["total_value_loss_pct"] = no_vol["vsi_core_loss_pct"]
    r = _corridor_rank(no_vol, "value_survival_index")
    checks.append(_check_row("exclude_volatility_penalty", base_rank, r, baseline, no_vol))

    # 3. RPW fee + FX margin only
    rpw_only = baseline.copy()
    rpw_loss = rpw_only["explicit_fee_loss_pct"] + rpw_only["fx_spread_loss_pct"]
    rpw_only["total_value_loss_pct"] = rpw_loss.clip(0, 0.5)
    rpw_only["value_survival_index"] = 100 * (1 - rpw_only["total_value_loss_pct"])
    r = _corridor_rank(rpw_only, "value_survival_index")
    checks.append(_check_row("rpw_fee_fx_margin_only", base_rank, r, baseline, rpw_only))

    # 4. RPW total cost vs reconstructed
    if "total_cost_pct" in corridor_prices.columns:
        recon = baseline.copy()
        recon["rpw_total_cost_pct"] = corridor_prices["total_cost_pct"].values[: len(recon)]
        recon["reconstructed_pct"] = recon["explicit_fee_loss_pct"] + recon["fx_spread_loss_pct"]
        recon["rpw_vs_recon_diff"] = recon["rpw_total_cost_pct"] - recon["reconstructed_pct"]
        mean_diff = float(recon["rpw_vs_recon_diff"].mean())
        checks.append({
            "check_id": "rpw_total_vs_reconstructed",
            "description": "Compare RPW total cost to fee + FX margin",
            "rank_stability_spearman": float("nan"),
            "mean_vsi_change": mean_diff * 100,
            "n_corridors": recon["corridor"].nunique(),
            "notes": "Difference in percentage points; lower is better alignment.",
        })

    # 5. Winsorize extreme losses at 95th percentile
    wins = baseline.copy()
    cap = wins["total_value_loss_pct"].quantile(0.95)
    wins["total_value_loss_pct"] = wins["total_value_loss_pct"].clip(upper=cap)
    wins["value_survival_index"] = 100 * (1 - wins["total_value_loss_pct"])
    r = _corridor_rank(wins, "value_survival_index")
    checks.append(_check_row("winsorize_extreme_losses", base_rank, r, baseline, wins))

    # 6. Send amount comparison if $500 data exists
    if "send_amount_usd" in corridor_prices.columns:
        amounts = corridor_prices["send_amount_usd"].dropna().unique()
        if len(amounts) >= 2:
            for amt in sorted(amounts)[:2]:
                sub = corridor_prices[corridor_prices["send_amount_usd"] == amt]
                if len(sub) >= 5:
                    v = calculate_vsi_for_corridors(
                        sub, fx_rates, macro, trust_scores, dollar_dependency,
                        mock_data_flag=mock_data_flag,
                    )
                    r = _corridor_rank(v, "vsi_risk_adjusted")
                    checks.append(_check_row(
                        f"send_amount_{int(amt)}",
                        base_rank, r, baseline, v,
                    ))

    # 7. Provider type comparison
    if "provider_type" in corridor_prices.columns:
        for ptype in corridor_prices["provider_type"].dropna().unique()[:4]:
            sub = corridor_prices[corridor_prices["provider_type"] == ptype]
            if len(sub) >= 5:
                v = calculate_vsi_for_corridors(
                    sub, fx_rates, macro, trust_scores, dollar_dependency,
                    mock_data_flag=mock_data_flag,
                )
                r = _corridor_rank(v, "vsi_risk_adjusted")
                checks.append(_check_row(
                    f"provider_{str(ptype).lower().replace(' ', '_')}",
                    base_rank, r, baseline, v,
                ))

    return pd.DataFrame(checks)


def _check_row(
    check_id: str,
    base_rank: pd.Series,
    alt_rank: pd.Series,
    baseline: pd.DataFrame,
    alt: pd.DataFrame,
) -> dict:
    spearman = _rank_correlation(base_rank, alt_rank)
    base_vsi = baseline.groupby("corridor")["vsi_risk_adjusted"].mean()
    alt_vsi = alt.groupby("corridor")["vsi_risk_adjusted"].mean() if "vsi_risk_adjusted" in alt.columns else alt.groupby("corridor")["value_survival_index"].mean()
    common = base_vsi.index.intersection(alt_vsi.index)
    mean_change = float((alt_vsi.reindex(common) - base_vsi.reindex(common)).mean()) if len(common) else float("nan")
    stable = spearman >= 0.85 if not np.isnan(spearman) else False
    return {
        "check_id": check_id,
        "description": check_id.replace("_", " "),
        "rank_stability_spearman": round(spearman, 3) if not np.isnan(spearman) else None,
        "mean_vsi_change": round(mean_change, 2),
        "n_corridors": len(common),
        "robust": stable,
        "notes": "Robust if Spearman rank correlation ≥ 0.85 across specifications.",
    }
