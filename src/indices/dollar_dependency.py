"""
Dollar Dependency Index — measures reliance on USD infrastructure.
"""

from __future__ import annotations

import pandas as pd

from src.data.sovereignty import sovereignty_lookup
from src.indices._utils import normalize_index
from src.indices.value_survival import calculate_dollar_dependency_drag


DOLLAR_DEPENDENCY_LIMITATIONS = (
    "USD debt share, invoicing, and sanctions exposure use manual research estimates where noted. "
    "Drag formula is a transparent placeholder — not a measured payment rail cost."
)


def calculate_dollar_dependency_drag_from_score(score: float) -> float:
    """VSI drag component from dollar dependency score 0–100."""
    return calculate_dollar_dependency_drag(score)


def explain_dollar_dependency(row: pd.Series) -> str:
    country = row.get("country", "Unknown")
    score = float(row.get("dollar_dependency_score", 0))
    drag = calculate_dollar_dependency_drag(score) * 100
    interp = row.get("interpretation", "")
    return (
        f"{country}: dollar dependency score {score:.1f}/100 ({interp}). "
        f"Estimated VSI drag ≈ {drag:.3f}% of cross-border value. "
        "Higher USD infrastructure reliance increases friction for value survival."
    )


def calculate_dollar_dependency_row(
    macro_row: pd.Series,
    market_row: pd.Series | None = None,
    flow_weight: float = 0.0,
    sovereignty: dict | None = None,
) -> dict:
    imports = float(macro_row.get("imports_gdp") or 0.3)
    remit = float(macro_row.get("remittances_gdp") or 0)
    debt = float(macro_row.get("external_debt_gdp") or 0.5)
    ca = float(macro_row.get("current_account_gdp") or -0.03)

    dollar_pair = float(market_row.get("dollar_pair_share") if market_row is not None else 0.7)
    liquidity = float(market_row.get("liquidity_score") if market_row is not None else 30)

    sov = sovereignty or {}
    usd_debt_share = float(sov.get("usd_debt_share") or min(debt * 0.6, 1.0))
    usd_invoicing = float(sov.get("usd_invoicing_share") or min(imports * 0.7, 1.0))
    reserves_usd = float(sov.get("reserves_usd_share") or 0.65)
    stablecoin = float(sov.get("stablecoin_exposure") or 0.05)
    sanctions_exposure = float(sov.get("sanctions_exposure") or 0.1)

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
        "dollar_debt_share": usd_debt_share,
        "usd_invoicing_share": usd_invoicing,
        "dollar_pair_share": dollar_pair,
        "reserves_usd_share": reserves_usd,
        "remittance_dependence": remit,
        "import_dependency": imports,
        "stablecoin_exposure": stablecoin,
        "sanctions_exposure": sanctions_exposure,
        "dollar_dependency_score": score,
        "interpretation": interp,
    }


def calculate_dollar_dependency_table(
    macro: pd.DataFrame,
    market_structure: pd.DataFrame,
    remittance_flows: pd.DataFrame | None = None,
    sovereignty_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    sov_map = sovereignty_lookup() if sovereignty_df is None else {
        str(r["country"]): r.to_dict() for _, r in sovereignty_df.iterrows()
    }

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
        sov = sov_map.get(row["country"], {})
        scores = calculate_dollar_dependency_row(row, mkt, fw, sov)
        scores["dollar_dependency_drag_pct"] = calculate_dollar_dependency_drag(scores["dollar_dependency_score"])
        scores["explanation"] = explain_dollar_dependency(pd.Series({**row.to_dict(), **scores}))
        rows.append({**row.to_dict(), **scores})
    out = pd.DataFrame(rows)
    out["dollar_dependency_index"] = normalize_index(out["dollar_dependency_score"], invert=False)
    return out
