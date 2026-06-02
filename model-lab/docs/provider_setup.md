# Model Lab — Provider Setup

## Supported providers

| Provider | Type | Config |
|----------|------|--------|
| Ollama | Local | `MODEL_PROVIDER=ollama`, `OLLAMA_BASE_URL` |
| LM Studio | Local OpenAI-compatible | `MODEL_PROVIDER=lmstudio` |
| OpenAI | Hosted | `OPENAI_API_KEY` required |
| Anthropic | Hosted only | `ANTHROPIC_API_KEY` — **cannot download Claude locally** |

Copy `model-lab/config/providers.example.env` to `.env` (never commit secrets).

## Smoke test

```bash
npm run model:smoke
```

Fails gracefully if Ollama is not running — build does not require local LLM.

## Registry

See `model-lab/config/model_registry.json`.
