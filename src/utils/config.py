"""Configuration loader for the FX research terminal."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .paths import ROOT

DEFAULT_CONFIG = ROOT / "config.yaml"


def load_terminal_config(path: Path | None = None) -> dict[str, Any]:
    """Load lab config.yaml with terminal defaults."""
    cfg_path = path or DEFAULT_CONFIG
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    terminal = cfg.setdefault("fx_terminal", {})
    terminal.setdefault("history_years", cfg.get("data", {}).get("history_years", 10))
    terminal.setdefault("train_years", cfg.get("backtest", {}).get("train_years", 5))
    terminal.setdefault("test_years", cfg.get("backtest", {}).get("test_years", 1))
    terminal.setdefault("risk_per_trade_pct", 0.0075)
    terminal.setdefault("min_reward_risk", 2.0)
    terminal.setdefault("ollama_base_url", "http://localhost:11434")
    terminal.setdefault("ollama_model", "llama3.1:8b")
    return cfg
