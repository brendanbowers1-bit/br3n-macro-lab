"""
BR3N Value Survival Index (VSI) — credible empirical measurement framework.

VSI = 100 × Real Usable Value Delivered / Original Value Sent

Three specifications:
- VSI_CORE: fees, spread, timing, inflation, payout (empirically clean baseline)
- VSI_RISK_ADJUSTED: CORE + FX volatility exposure
- VSI_EXTENDED: RISK_ADJUSTED + dollar drag + trust discount (extended spec)

Research-only. Not investment advice. Not a trading signal.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config.research_settings import (
    BASELINE_DAYS_HELD,
    HEDGE_ACCESS_SCORE_HOUSEHOLD,
    METHODOLOGY_VERSION,
    PAYOUT_FRICTION_DEFAULTS,
    SENSITIVITY_CASES,
    TIMING_RISK_WEIGHT,
    VOLATILITY_WEIGHT,
    is_credible_mode,
)
from src.indices._utils import rank_series

VSI_LIMITATIONS = (
    "Measurement framework only — estimates cross-border value loss under stated assumptions. "
    "Does not prove causal welfare effects without identification. "
    "Not investment advice, not a trading signal, not a price forecast. "
    "Extended specification components (dollar drag, trust discount) are model-based adjustments."
)


def calculate_explicit_fee_loss(fee_pct: float) -> float:
    return max(float(fee_pct or 0), 0.0)


def calculate_fx_spread_loss(fx_margin_pct: float) -> float:
    return max(float(fx_margin_pct or 0), 0.0)


def calculate_timing_loss(
    transfer_speed_days: float,
    fx_daily_volatility: float,
    sensitivity_case: str = "baseline",
) -> float:
    days = max(float(transfer_speed_days or 0), 0)
    vol = max(float(fx_daily_volatility or 0.01), 0.0001)
    w = TIMING_RISK_WEIGHT.get(sensitivity_case, TIMING_RISK_WEIGHT["baseline"])
    return min(days * vol * w, 0.05)


def calculate_volatility_loss(
    volatility_30d: float,
    hedge_access_score: float = HEDGE_ACCESS_SCORE_HOUSEHOLD,
    sensitivity_case: str = "baseline",
) -> float:
    vol = max(float(volatility_30d or 0), 0)
    hedge = min(max(float(hedge_access_score), 0), 1)
    w = VOLATILITY_WEIGHT.get(sensitivity_case, VOLATILITY_WEIGHT["baseline"])
    return vol * (1 - hedge) * w


def calculate_inflation_erosion(inflation_yoy: float, days_held: float = BASELINE_DAYS_HELD) -> float:
    infl = max(float(inflation_yoy or 0), 0)
    days = max(float(days_held or BASELINE_DAYS_HELD), 0)
    return infl * days / 365.0


def calculate_payout_friction(
    payout_method: str | None,
    manual_payout_friction_pct: float | None = None,
) -> tuple[float, str]:
    if manual_payout_friction_pct is not None and pd.notna(manual_payout_friction_pct):
        return max(float(manual_payout_friction_pct), 0), "manual_observed"
    key = str(payout_method or "unknown").lower().replace(" ", "_")
    for k, v in PAYOUT_FRICTION_DEFAULTS.items():
        if k in key:
            return v, "payout_method_default"
    return PAYOUT_FRICTION_DEFAULTS["unknown"], "payout_method_default"


def calculate_dollar_dependency_drag(dollar_dependency_score: float) -> float:
    score = min(max(float(dollar_dependency_score or 0), 0), 100)
    return score / 100.0 * 0.0075


def calculate_trust_discount(currency_trust_score: float) -> float:
    score = min(max(float(currency_trust_score or 50), 0), 100)
    return (100 - score) / 100.0 * 0.01


def _daily_vol_from_30d(volatility_30d: float) -> float:
    return float(volatility_30d or 0.12) / np.sqrt(252)


def _loss_from_components(components: dict[str, float]) -> float:
    return min(sum(components.values()), 0.50)


def calculate_vsi(real_usable_value_delivered_pct: float) -> float:
    return 100.0 * max(float(real_usable_value_delivered_pct or 0), 0.0)


def calculate_value_loss_usd_per_100(total_value_loss_pct: float) -> float:
    return 100.0 * float(total_value_loss_pct or 0)


def classify_vsi(vsi_score: float) -> str:
    v = float(vsi_score or 0)
    if v >= 95:
        return "High value survival (estimated)"
    if v >= 90:
        return "Moderate value leakage (estimated)"
    if v >= 80:
        return "High value leakage (estimated)"
    return "Severe value destruction (estimated)"


def _resolve_source(field: str, row: pd.Series, tables: dict | None) -> str:
    src = str(row.get("source", "") or "")
    tier = "mock_synthetic" if "mock" in src.lower() else ""
    if field in ("fee_pct", "fx_margin_pct", "transfer_speed_days"):
        if "rpw" in src.lower() or "world_bank" in src.lower():
            return "world_bank_rpw"
        if tier:
            return "mock_assumed"
        return "world_bank_rpw_curated"
    if field == "volatility_30d":
        return "imf_fx_lab_cache" if not tier else "mock_assumed"
    if field == "inflation_yoy":
        return "world_bank_api_macro" if not tier else "mock_assumed"
    if field == "payout_friction":
        return row.get("payout_friction_source", "payout_method_default")
    if field == "dollar_dependency":
        return "bis_sovereignty_extended_spec"
    if field == "trust_discount":
        return "currency_trust_extended_spec"
    return "assumed"


def trace_sources(row: pd.Series, tables: dict | None = None) -> dict:
    src = str(row.get("source", "") or "")
    mock = "mock" in src.lower() or "synthetic" in src.lower()
    manual = any(
        str(row.get(c, "")).endswith("_default") or str(row.get(c, "")) == "manual"
        for c in ("payout_friction_source",)
    )
    return {
        "fee_source": _resolve_source("fee_pct", row, tables),
        "fx_margin_source": _resolve_source("fx_margin_pct", row, tables),
        "inflation_source": _resolve_source("inflation_yoy", row, tables),
        "fx_volatility_source": _resolve_source("volatility_30d", row, tables),
        "remittance_volume_source": "world_bank_knomad_curated",
        "payout_friction_source": row.get("payout_friction_source", "payout_method_default"),
        "dollar_dependency_source": "manual_research_bis_extended_spec",
        "trust_score_source": "macro_sovereignty_extended_spec",
        "methodology_version": METHODOLOGY_VERSION,
        "mock_data_flag": mock,
        "manual_assumption_flag": manual or (not mock and "curated" in src.lower()),
    }


def calculate_vsi_row(
    row: pd.Series,
    sensitivity_case: str = "baseline",
    include_extended: bool = True,
) -> dict:
    fee = calculate_explicit_fee_loss(row.get("fee_pct"))
    spread = calculate_fx_spread_loss(row.get("fx_margin_pct"))
    vol_30d = float(row.get("volatility_30d") or row.get("fx_volatility_30d") or 0.12)
    daily_vol = _daily_vol_from_30d(vol_30d)
    speed = float(row.get("transfer_speed_days") or 1)
    infl = float(row.get("inflation_yoy") or 0.05)
    hedge = float(row.get("hedge_access_score") or HEDGE_ACCESS_SCORE_HOUSEHOLD)

    timing = calculate_timing_loss(speed, daily_vol, sensitivity_case)
    vol_loss = calculate_volatility_loss(vol_30d, hedge, sensitivity_case)
    inflation = calculate_inflation_erosion(infl, days_held=speed + 1)
    payout, payout_src = calculate_payout_friction(
        row.get("payout_method"), row.get("manual_payout_friction_pct")
    )

    core_components = {
        "explicit_fee_loss_pct": fee,
        "fx_spread_loss_pct": spread,
        "timing_loss_pct": timing,
        "inflation_erosion_pct": inflation,
        "payout_friction_pct": payout,
    }
    core_loss = _loss_from_components(core_components)
    core_delivered = max(1.0 - core_loss, 0)
    vsi_core = calculate_vsi(core_delivered)

    risk_components = {**core_components, "volatility_loss_pct": vol_loss}
    risk_loss = _loss_from_components(risk_components)
    risk_delivered = max(1.0 - risk_loss, 0)
    vsi_risk = calculate_vsi(risk_delivered)

    dollar_drag = calculate_dollar_dependency_drag(row.get("dollar_dependency_score", 50))
    trust = calculate_trust_discount(row.get("currency_trust_score", 50))
    ext_components = {
        **risk_components,
        "dollar_dependency_drag_pct": dollar_drag if include_extended else 0.0,
        "trust_discount_pct": trust if include_extended else 0.0,
    }
    ext_loss = _loss_from_components(ext_components)
    ext_delivered = max(1.0 - ext_loss, 0)
    vsi_extended = calculate_vsi(ext_delivered)

    # Primary reported index = risk-adjusted (baseline empirical spec)
    primary_loss = risk_loss
    primary_delivered = risk_delivered
    vsi_primary = vsi_risk

    out = {
        **core_components,
        "volatility_loss_pct": vol_loss,
        "dollar_dependency_drag_pct": ext_components["dollar_dependency_drag_pct"],
        "trust_discount_pct": ext_components["trust_discount_pct"],
        "vsi_core_loss_pct": core_loss,
        "vsi_core": vsi_core,
        "vsi_risk_adjusted_loss_pct": risk_loss,
        "vsi_risk_adjusted": vsi_risk,
        "vsi_extended_loss_pct": ext_loss,
        "vsi_extended": vsi_extended,
        "total_value_loss_pct": primary_loss,
        "real_usable_value_delivered_pct": primary_delivered,
        "value_survival_index": vsi_primary,
        "value_loss_usd_per_100": calculate_value_loss_usd_per_100(primary_loss),
        "interpretation": classify_vsi(vsi_primary),
        "sensitivity_case": sensitivity_case,
        "payout_friction_source": payout_src,
        "limitations": VSI_LIMITATIONS,
    }
    out.update(trace_sources(row))
    return out


def calculate_vsi_for_corridors(
    corridor_prices: pd.DataFrame,
    fx_rates: pd.DataFrame | None = None,
    macro: pd.DataFrame | None = None,
    trust_scores: pd.DataFrame | None = None,
    dollar_dependency: pd.DataFrame | None = None,
    mock_data_flag: bool = False,
    sensitivity_case: str = "baseline",
) -> pd.DataFrame:
    df = corridor_prices.copy()
    if "year" not in df.columns and "date" in df.columns:
        df["year"] = pd.to_datetime(df["date"]).dt.year

    if fx_rates is not None and not fx_rates.empty:
        vol_map = fx_rates.sort_values("date").groupby("currency")["volatility_30d"].last().to_dict()
        df["volatility_30d"] = df["receiver_currency"].map(vol_map).fillna(0.12)

    if macro is not None and not macro.empty:
        infl_map = macro.sort_values("date").groupby("country")["inflation_yoy"].last().to_dict()
        df["inflation_yoy"] = df["receiver_country"].map(infl_map).fillna(0.05)

    if trust_scores is not None and not trust_scores.empty:
        trust_map = trust_scores.set_index("country")["currency_trust_score"].to_dict()
        df["currency_trust_score"] = df["receiver_country"].map(trust_map).fillna(50)

    if dollar_dependency is not None and not dollar_dependency.empty:
        dep_map = dollar_dependency.set_index("country")["dollar_dependency_score"].to_dict()
        df["dollar_dependency_score"] = df["receiver_country"].map(dep_map).fillna(50)

    if mock_data_flag:
        df["source"] = df.get("source", "mock_synthetic")

    components = df.apply(
        lambda r: calculate_vsi_row(r, sensitivity_case=sensitivity_case),
        axis=1,
        result_type="expand",
    )
    out = pd.concat([df, components], axis=1)
    out["original_value_sent_usd"] = out.get("send_amount_usd", 200.0)
    out["data_mode"] = "demo" if mock_data_flag else "real"
    out["mock_data_flag"] = bool(mock_data_flag)
    out["rank"] = rank_series(out["total_value_loss_pct"])
    return out
