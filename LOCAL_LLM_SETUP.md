# Local LLM Setup — Bowers Frontier FX Research Terminal

The FX research terminal uses **Ollama** for local LLM tasks. LLMs do **not** generate trading signals directly. They:

- Explain model outputs
- Classify central bank tone and news events
- Generate trade memos for research review
- Sanity-check whether signals are economically plausible

Statistical/ML models produce the actual signals. The risk engine decides whether a trade idea is acceptable.

---

## Install Ollama

1. Download from [https://ollama.com](https://ollama.com)
2. Install and start the Ollama app (daemon runs on port **11434**)

## Pull recommended models

```bash
ollama run qwen2.5-coder:7b
ollama run deepseek-r1:8b
ollama run llama3.1:8b
ollama run nomic-embed-text
```

Larger variants (14b) if you have sufficient RAM/GPU:

```bash
ollama run qwen2.5-coder:14b
ollama run deepseek-r1:14b
```

## Recommended use

| Model | Role |
|-------|------|
| **Qwen Coder** | Code, pipeline building, refactoring |
| **DeepSeek R1** | Reasoning through trade thesis and macro narrative |
| **Llama 3.1** | General macro explanation and memo drafting |
| **nomic-embed-text** | Local document search / embeddings |

## Configure in FX Lab

Default settings in `config.yaml` under `fx_terminal`:

```yaml
fx_terminal:
  ollama_base_url: "http://localhost:11434"
  ollama_model: "llama3.1:8b"
```

Or set when creating `OllamaClient(base_url=..., model=...)`.

## Test connection

```bash
curl http://localhost:11434/api/tags
python -c "from src.llm.ollama_client import OllamaClient; c=OllamaClient(); print(c.is_available())"
```

## Generate a trade memo

```python
from src.llm.memo_generator import generate_trade_memo

memo = generate_trade_memo({
    "pair": "USD/MXN",
    "direction": "short",
    "horizon": 5,
    "model_name": "momentum",
    "probability_up": 0.42,
    "expected_return": -0.001,
    "confidence": 0.25,
    "regime": "usd_bull",
    "regime_description": "Broad USD strength",
    "carry_score": 3.5,
    "ret_20d": -0.02,
    "vol_20d": 0.14,
    "stop_loss": 20.5,
    "take_profit": 19.5,
    "reward_risk": 2.0,
    "trade_decision": "watchlist",
})
print(memo)
```

Memos save to `reports/trade_memos/`.

---

## Important

- LLMs can hallucinate macro facts — always verify against data
- Do not connect LLM output directly to execution
- Use for research documentation, classification, and explanation only
