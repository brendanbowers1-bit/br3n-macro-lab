const { BaseProvider } = require("./base_provider");

class AnthropicProvider extends BaseProvider {
  constructor(config) {
    super(config);
    this.apiKey = config.apiKey || process.env.ANTHROPIC_API_KEY;
    this.model = config.model || process.env.MODEL_NAME || "claude-sonnet-4-20250514";
  }

  async healthCheck() {
    if (!this.apiKey) return { ok: false, message: "ANTHROPIC_API_KEY not set (hosted API only)" };
    return { ok: true, message: "Anthropic API key present — hosted only, not local" };
  }

  async generate({ prompt, system, model, temperature = 0.2, maxTokens = 1024 }) {
    if (!this.apiKey) throw new Error("ANTHROPIC_API_KEY not set");
    const started = Date.now();
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": this.apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: model || this.model,
        max_tokens: maxTokens,
        temperature,
        system: system || "You are a research assistant for Bowers Frontier Macro Labs.",
        messages: [{ role: "user", content: prompt }],
      }),
    });
    if (!res.ok) throw new Error(`Anthropic error ${res.status}: ${await res.text()}`);
    const data = await res.json();
    const text = (data.content || []).map((c) => c.text || "").join("");
    return {
      text,
      model: model || this.model,
      provider: "anthropic",
      latency_ms: Date.now() - started,
    };
  }
}

module.exports = { AnthropicProvider };
