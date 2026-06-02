const { BaseProvider } = require("./base_provider");

class OllamaProvider extends BaseProvider {
  constructor(config) {
    super(config);
    this.baseUrl = config.baseUrl || process.env.OLLAMA_BASE_URL || "http://localhost:11434";
    this.model = config.model || process.env.MODEL_NAME || "qwen2.5-coder:7b";
  }

  async healthCheck() {
    try {
      const res = await fetch(`${this.baseUrl}/api/tags`);
      if (!res.ok) return { ok: false, message: `Ollama HTTP ${res.status}` };
      return { ok: true, message: "Ollama reachable" };
    } catch (e) {
      return { ok: false, message: e.message };
    }
  }

  async generate({ prompt, system, model, temperature = 0.2, maxTokens = 1024 }) {
    const started = Date.now();
    const body = {
      model: model || this.model,
      prompt: system ? `${system}\n\n${prompt}` : prompt,
      stream: false,
      options: { temperature, num_predict: maxTokens },
    };
    const res = await fetch(`${this.baseUrl}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`Ollama error ${res.status}: ${await res.text()}`);
    const data = await res.json();
    return {
      text: data.response || "",
      model: body.model,
      provider: "ollama",
      latency_ms: Date.now() - started,
    };
  }
}

module.exports = { OllamaProvider };
