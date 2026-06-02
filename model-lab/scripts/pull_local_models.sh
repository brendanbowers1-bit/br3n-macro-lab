#!/usr/bin/env bash
# Pull recommended local models via Ollama (safe defaults)
set -euo pipefail
if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama not installed. Install from https://ollama.com then re-run."
  exit 0
fi
for model in qwen2.5-coder:7b llama3.1:8b mistral; do
  echo "Pulling $model ..."
  ollama pull "$model" || echo "Warning: failed to pull $model"
done
# Larger models (commented — uncomment if you have RAM)
# ollama pull qwen2.5-coder:32b
# ollama pull llama3.1:70b
# ollama pull deepseek-r1
echo "model:pull complete"
