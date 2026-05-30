"""
FX desk risk memo generator — markdown decision-support memos.

Research and risk-framing only. Not investment advice.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Union

ROOT = Path(__file__).resolve().parents[1]
MEMO_DIR = ROOT / "reports" / "fx_desk_memos"


def generate_fx_desk_memo(
    scorecard: Union[Dict[str, Any], Any],
    output_path: Path,
) -> Path:
    """
    Write a corridor FX desk risk memo from a scorecard dictionary.

    Saves to reports/fx_desk_memos/{corridor_id}_fx_desk_memo.md by default.
    """
    sc = dict(scorecard) if not isinstance(scorecard, dict) else scorecard
    cid = sc.get("corridor_id", "US_MX")
    pair = sc.get("pair_label", "USD/MXN")

    lines = [
        "# FX Desk Risk Memo",
        "",
        f"**Corridor:** {cid} / {pair}",
        "",
        "*Research and risk-framing only. Not investment advice. Not a trading instruction.*",
        "",
        "## Market State",
        "",
        f"- **Latest regime:** {sc.get('latest_regime', '—')}",
        f"- **Market summary:** {sc.get('market_state_summary', '—')}",
        f"- **Crisis risk level:** {sc.get('crisis_risk_level', '—')}",
        f"- **Overall desk risk:** {sc.get('overall_desk_risk_level', '—')}",
        f"- **Data quality:** {sc.get('data_quality_warning', '—')}",
        "",
        "## Key Desk Questions",
        "",
        "### 1. Exposure",
        "What exposure needs to be confirmed by currency, value date, entity, and counterparty?",
        "",
        "### 2. Hedge Timing",
        sc.get("hedge_timing_posture", "—"),
        "",
        "### 3. Pricing",
        f"**Customer pricing posture:** {sc.get('customer_pricing_posture', '—')}",
        "",
        "### 4. Liquidity and Prefunding",
        f"**Liquidity:** {sc.get('liquidity_risk_posture', '—')}",
        "",
        f"**Prefunding:** {sc.get('prefunding_posture', '—')}",
        "",
        "### 5. Settlement",
        sc.get("settlement_risk_posture", "—"),
        "",
        "### 6. Crisis / Escalation",
        f"Crisis risk level: **{sc.get('crisis_risk_level', '—')}**. "
        "Escalate if liquidity, spreads, or payout obligations deteriorate beyond policy.",
        "",
        "### 7. Speculation Control",
        sc.get("speculation_control_warning", "—"),
        "",
        "## Summary",
        "",
        sc.get("plain_language_summary", "—"),
        "",
        "## Disclaimer",
        "",
        sc.get(
            "disclaimer",
            "Research and risk-framing only. Not investment advice. Not a trading instruction.",
        ),
    ]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
