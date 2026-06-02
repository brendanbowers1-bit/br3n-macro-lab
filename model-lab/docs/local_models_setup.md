# Local Models Setup (Mac)

## Ollama

1. Install from https://ollama.com
2. `ollama serve` (or use app)
3. `npm run model:pull` — pulls qwen2.5-coder:7b, llama3.1:8b, mistral
4. `MODEL_PROVIDER=ollama MODEL_NAME=qwen2.5-coder:7b npm run model:smoke`

**RAM guidance:** 7B–8B models ~8–16 GB; 32B+ requires significant unified memory.

## LM Studio

1. Install LM Studio
2. Load a model and start local server (default port 1234)
3. `MODEL_PROVIDER=lmstudio npm run model:smoke`

## Common errors

- **Connection refused:** Ollama/LM Studio not running
- **Model not found:** Run `ollama pull <model>` or select model in LM Studio
- **Missing API key:** Expected for OpenAI/Anthropic until keys are set
