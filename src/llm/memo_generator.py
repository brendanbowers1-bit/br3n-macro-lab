"""Trade memo generation via local LLM."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.llm.ollama_client import OllamaClient
from src.llm.prompts import TRADE_MEMO_PROMPT
from src.utils.paths import TRADE_MEMOS_DIR


def build_memo_prompt(context: dict[str, Any]) -> str:
    return TRADE_MEMO_PROMPT.format(
        pair=context.get("pair", "N/A"),
        direction=context.get("direction", "neutral"),
        horizon=context.get("horizon", 5),
        model_name=context.get("model_name", "unknown"),
        probability_up=float(context.get("probability_up", 0.5)),
        expected_return=float(context.get("expected_return", 0)),
        confidence=float(context.get("confidence", 0)),
        regime=context.get("regime", "unknown"),
        regime_description=context.get("regime_description", ""),
        carry_score=float(context.get("carry_score", 0)),
        ret_20d=float(context.get("ret_20d", 0)),
        vol_20d=float(context.get("vol_20d", 0)),
        stop_loss=float(context.get("stop_loss", 0)),
        take_profit=float(context.get("take_profit", 0)),
        reward_risk=float(context.get("reward_risk", 0)),
        trade_decision=context.get("trade_decision", "watchlist"),
    )


def generate_trade_memo(
    context: dict[str, Any],
    client: OllamaClient | None = None,
    *,
    save: bool = True,
) -> str:
    """Generate and optionally save a trade memo markdown file."""
    client = client or OllamaClient()
    prompt = build_memo_prompt(context)
    system = (
        "You are an institutional FX research assistant. "
        "Research and education only. Not investment advice. No live trading."
    )
    memo = client.generate(prompt, system=system)
    if save:
        pair = str(context.get("pair", "UNKNOWN")).replace("/", "_").replace("=", "")
        path = TRADE_MEMOS_DIR / f"memo_{pair}_{context.get('horizon', 5)}d.md"
        path.write_text(memo, encoding="utf-8")
    return memo
