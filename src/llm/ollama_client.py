"""
Ollama client for local LLM research tasks.

Calls http://localhost:11434 — requires Ollama running locally.
LLMs explain and classify; they do NOT generate trading signals directly.
"""

from __future__ import annotations

import json
from typing import Any, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

DEFAULT_BASE = "http://localhost:11434"


class OllamaClient:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE,
        model: str = "llama3.1:8b",
        timeout: int = 120,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            req = Request(f"{self.base_url}/api/tags", method="GET")
            with urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except (URLError, OSError, TimeoutError):
            return False

    def generate(self, prompt: str, *, system: str | None = None, temperature: float = 0.2) -> str:
        """Call /api/generate and return response text."""
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system
        data = json.dumps(payload).encode("utf-8")
        req = Request(
            f"{self.base_url}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return str(body.get("response", ""))
        except (URLError, OSError, TimeoutError) as exc:
            return f"[Ollama unavailable: {exc}. Start Ollama and run: ollama run {self.model}]"

    def embed(self, text: str, model: str = "nomic-embed-text") -> list[float]:
        """Call /api/embeddings."""
        payload = {"model": model, "prompt": text}
        data = json.dumps(payload).encode("utf-8")
        req = Request(
            f"{self.base_url}/api/embeddings",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=self.timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return list(body.get("embedding", []))
