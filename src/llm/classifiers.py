"""LLM classifiers for news and central bank text."""

from __future__ import annotations

from src.llm.ollama_client import OllamaClient
from src.llm.prompts import CENTRAL_BANK_TONE_PROMPT, MODEL_SANITY_CHECK_PROMPT, NEWS_EVENT_PROMPT


def classify_central_bank_tone(text: str, client: OllamaClient | None = None) -> str:
    client = client or OllamaClient()
    return client.generate(
        CENTRAL_BANK_TONE_PROMPT.format(text=text),
        system="FX research classifier. Output structured text, not trading advice.",
    )


def classify_news_event(text: str, client: OllamaClient | None = None) -> str:
    client = client or OllamaClient()
    return client.generate(
        NEWS_EVENT_PROMPT.format(text=text),
        system="FX news classifier for research. Not investment advice.",
    )


def sanity_check_model_signal(context: dict, client: OllamaClient | None = None) -> str:
    client = client or OllamaClient()
    return client.generate(
        MODEL_SANITY_CHECK_PROMPT.format(
            pair=context.get("pair", ""),
            signal=context.get("signal", ""),
            probability_up=context.get("probability_up", 0.5),
            features=context.get("features", {}),
        ),
        system="Skeptical quant researcher reviewing model output.",
    )
