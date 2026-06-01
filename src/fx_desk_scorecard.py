"""
FX desk decision-support scorecard — research and risk-framing only.

Not a recommendation engine. Does not replace policy, approvals, or compliance.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

DISCLAIMER = (
    "Bowers Frontier Macro Labs is an independent research project. It is not affiliated with, endorsed by, "
    "or sponsored by any employer, financial institution, payment company, trading platform, "
    "or data vendor. Research and risk-framing only. Not investment advice. Not a trading instruction. "
    "Requires human review, exposure systems, and policy controls."
)


def _regime_family(regime: Optional[str]) -> str:
    if not regime:
        return ""
    r = str(regime).upper()
    if "R1" in r:
        return "R1"
    if "R2" in r:
        return "R2"
    if "R3" in r:
        return "R3"
    if "R4" in r:
        return "R4"
    return r


def _hedge_timing_posture(regime: Optional[str]) -> str:
    fam = _regime_family(regime)
    if fam == "R2":
        return "Orderly trend. Consider gradual hedge adjustment within policy limits."
    if fam == "R1":
        return (
            "High-volatility trend. Avoid one-shot hedge decisions. "
            "Consider tranches, options, or escalation."
        )
    if fam == "R3":
        return "Choppy high-volatility range. Avoid over-adjustment and review spread/liquidity risk."
    if fam == "R4":
        return "Quiet range. Maintain base hedge discipline; avoid unnecessary hedge churn."
    return "Regime unknown. Confirm market state before hedge action."


def _customer_pricing_posture(regime: Optional[str], flow_window: bool) -> str:
    fam = _regime_family(regime)
    if fam == "R1":
        return "Defensive — elevated volatility surcharge review recommended."
    if fam == "R3":
        return "Defensive — choppy conditions; widen spread band review."
    if flow_window:
        return "Elevated review — flow-pressure window; monitor competitive spread vs liquidity."
    if fam == "R2":
        return "Normal with trend awareness — monitor hedge cost pass-through."
    return "Normal — standard spread discipline unless data quality fails."


def _liquidity_risk_posture(regime: Optional[str], flow_window: bool) -> str:
    fam = _regime_family(regime)
    if fam in ("R1", "R3"):
        return "Elevated — review executable rates and payout liquidity."
    if flow_window:
        return "Elevated — flow window may increase payout demand."
    return "Standard — routine liquidity monitoring."


def _prefunding_posture(flow_window: bool, regime: Optional[str]) -> str:
    if flow_window:
        return (
            "Flow-pressure window active. Review payout liquidity and prefunding buffers."
        )
    fam = _regime_family(regime)
    if fam == "R1":
        return "Review buffers — volatile trend may require higher prefunding headroom."
    return "Standard prefunding discipline unless corridor data warns otherwise."


def _settlement_risk_posture(flow_window: bool) -> str:
    if flow_window:
        return "Review value-date alignment — flow windows may compress settlement timing."
    return "Standard settlement calendar review."


def _crisis_risk_level(regime: Optional[str], volatility_state: Optional[str]) -> str:
    fam = _regime_family(regime)
    vol = (volatility_state or "").lower()
    if fam == "R1" or "high" in vol:
        return "Elevated"
    if fam == "R3":
        return "Moderate"
    return "Low"


def _speculation_control_warning(hedge_policy_result: Optional[str]) -> str:
    if hedge_policy_result and "no_change" in str(hedge_policy_result).lower():
        return (
            "Favor exposure-linked hedging. no_change_in_range reduces churn vs aggressive "
            "regime trading — verify action maps to documented exposure."
        )
    return (
        "All hedge actions must map to documented exposure and policy limits. "
        "Model signals are not directional trading instructions."
    )


def _data_quality_warning(data_quality_flag: Optional[str]) -> str:
    flag = (data_quality_flag or "").upper()
    if flag in ("WARNING", "FAIL", "FAILED", "BAD"):
        return "Do not make strong research conclusions until data quality is improved."
    if flag:
        return f"Data quality flag: {data_quality_flag}. Prototype data — upgrade for publication."
    return "Data quality not verified — assume Tier 4 prototype until official sources loaded."


def _overall_desk_risk_level(
    regime: Optional[str],
    flow_window: bool,
    data_quality_flag: Optional[str],
) -> str:
    flag = (data_quality_flag or "").upper()
    if flag in ("WARNING", "FAIL", "FAILED", "BAD"):
        return "High"
    fam = _regime_family(regime)
    if fam == "R1":
        return "High"
    if fam == "R3":
        return "Elevated"
    if flow_window and fam == "R2":
        return "Elevated"
    if fam == "R2":
        return "Moderate"
    if fam == "R4":
        return "Low" if not flow_window else "Moderate"
    return "Moderate"


def _market_state_summary(regime: Optional[str], volatility_state: Optional[str]) -> str:
    parts = []
    if regime:
        parts.append(f"Regime: {regime}")
    if volatility_state:
        parts.append(f"Volatility: {volatility_state}")
    return " · ".join(parts) if parts else "Market state not available."


def _plain_language_summary(
    regime: Optional[str],
    random_walk_status: Optional[str],
    overall_risk: str,
    hedge_posture: str,
) -> str:
    rw = random_walk_status or "Unknown"
    base = (
        f"Overall desk risk level is {overall_risk}. "
        f"Hedge timing posture: {hedge_posture.split('.')[0]}."
    )
    if rw.lower() in ("not beaten", "weak evidence", "unknown"):
        base += (
            " Forecast evidence is weak, but regime information may still be useful "
            "for hedge governance and risk framing."
        )
    else:
        base += (
            " Some conditional structure may exist — requires robustness testing "
            "and better data before directional confidence."
        )
    fam = _regime_family(regime)
    if fam == "R1":
        base += " High-volatility trend: treat as stress framing, not blind trend-following."
    return base


def build_fx_desk_scorecard(
    corridor_id: Optional[str] = None,
    pair_label: Optional[str] = None,
    latest_regime: Optional[str] = None,
    volatility_state: Optional[str] = None,
    flow_window: bool = False,
    data_quality_flag: Optional[str] = None,
    hedge_policy_result: Optional[str] = None,
    random_walk_status: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a research/risk-framing FX desk scorecard for one corridor.

    Not a recommendation engine — supports decision discipline only.
    """
    hedge_posture = _hedge_timing_posture(latest_regime)
    pricing_posture = _customer_pricing_posture(latest_regime, flow_window)
    liquidity_posture = _liquidity_risk_posture(latest_regime, flow_window)
    prefunding = _prefunding_posture(flow_window, latest_regime)
    settlement = _settlement_risk_posture(flow_window)
    crisis = _crisis_risk_level(latest_regime, volatility_state)
    dq_warn = _data_quality_warning(data_quality_flag)
    spec_warn = _speculation_control_warning(hedge_policy_result)
    overall = _overall_desk_risk_level(latest_regime, flow_window, data_quality_flag)
    summary = _plain_language_summary(
        latest_regime, random_walk_status, overall, hedge_posture
    )

    return {
        "corridor_id": corridor_id or "US_MX",
        "pair_label": pair_label or "USD/MXN",
        "latest_regime": latest_regime or "—",
        "market_state_summary": _market_state_summary(latest_regime, volatility_state),
        "hedge_timing_posture": hedge_posture,
        "customer_pricing_posture": pricing_posture,
        "liquidity_risk_posture": liquidity_posture,
        "prefunding_posture": prefunding,
        "settlement_risk_posture": settlement,
        "crisis_risk_level": crisis,
        "speculation_control_warning": spec_warn,
        "data_quality_warning": dq_warn,
        "overall_desk_risk_level": overall,
        "plain_language_summary": summary,
        "disclaimer": DISCLAIMER,
    }
