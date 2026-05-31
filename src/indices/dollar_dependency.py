"""
Dollar Dependency Index — measures reliance on USD infrastructure.
"""

from __future__ import annotations

import pandas as pd

from src.indices._utils import normalize_index


def calculate_dollar_dependency_row(
    macro_row: pd.Series,
    market_row: pd.Series | None = None,
    flow_weight: float = 0.0,
) -> dict:
    imports = float(macro_row.get("imports_gdp") or 0.3)
    remit = float(macro_row.get("remittances_gdp") or 0)
    debt = float(macro_row.get("external_debt_gdp") or 0.5)
    ca = float(macro_row.get("current_account_gdp") or -0.03)

    dollar_pair = float(market_row.get("dollar_pair_share") if market_row is not None else 0.7)
    turnover_share = float(market_row.get("global_turnover_share") if market_row is not None else 0.01)
    liquidity = float(market_row.get("liquidity_score") if market_row is not None else 30)

    # Placeholders — wire manual data later
    usd_debt_share = min(debt * 0.6, 1.0)
    usd_invoicing = min(imports * 0.7, 1.0)
    reserves_usd = 0.65
    stablecoin = 0.05
    sanctions_exposure = 0.1

    score = (
        usd_debt_share * 15
        + usd_invoicing * 15
        + dollar_pair * 20
        + (1 - liquidity / 100) * 10
        + remit * 100 * 0.15
        + max(-ca, 0) * 100 * 0.10
        + flow_weight * 10
        + stablecoin * 5
        + sanctions_exposure * 10
    )
    score = min(score, 100)

    if score < 30:
        interp = "low dependency"
    elif score < 55:
        interp = "moderate dependency"
    elif score < 75:
        interp = "high dependency"
    else:
        interp = "dollar constrained"

    return {
        "dollar_debt_share_ph": usd_debt_share,
        "usd_invoicing_ph": usd_invoicing,
        "dollar_pair_share": dollar_pair,
        "reserves_usd_ph": reserves_usd,
        "remittance_dependence": remit,
        "import_dependency": imports,
        "stablecoin_ph": stablecoin,
        "sanctions_exposure_ph": sanctions_exposure,
        "dollar_dependency_score": score,
        "interpretation": interp,
    }


def calculate_dollar_dependency_table(
    macro: pd.DataFrame,
    market_structure: pd.DataFrame,
    remittance_flows: pd.DataFrame | None = None,
) -> pd.DataFrame:
    latest_macro = macro.sort_values("date").groupby("country", as_index=False).tail(1)
    latest_mkt = market_structure.sort_values("year").groupby("currency", as_index=False).tail(1).set_index("currency")

    flow_dep = {}
    if remittance_flows is not None and not remittance_flows.empty:
        dep = remittance_flows.groupby("receiver_country")["remittance_share_gdp"].mean()
        flow_dep = dep.to_dict()

    rows = []
    for _, row in latest_macro.iterrows():
        mkt = latest_mkt.loc[row["currency"]] if row["currency"] in latest_mkt.index else None
        fw = flow_dep.get(row["country"], 0)
        scores = calculate_dollar_dependency_row(row, mkt, fw)
        rows.append({**row.to_dict(), **scores})
    out = pd.DataFrame(rows)
    out["dollar_dependency_index"] = normalize_index(out["dollar_dependency_score"], invert=False)
    return out
