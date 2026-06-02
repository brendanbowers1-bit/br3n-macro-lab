const { BaseProvider } = require("./base_provider");

class LMStudioProvider extends BaseProvider {
  constructor(config) {
    super(config);
    this.baseUrl = config.baseUrl || process.env.LMSTUDIO_BASE_URL || "http://localhost:1234/v1";
    this.model = config.model || process.env.MODEL_NAME || "local-model";
  }

  async healthCheck() {
    try {
      const res = await fetch(`${this.baseUrl}/models`);
      if (!res.ok) return { ok: false, message: `LM Studio HTTP ${res.status}` };
      return { ok: true, message: "LM Studio reachable" };
    } catch (e) {
      return { ok: false, message: e.message };
    }
  }

  async generate({ prompt, system, model, temperature = 0.2, maxTokens = 1024 }) {
    const started = Date.now();
    const messages = [];
    if (system) messages.push({ role: "system", content: system });
    messages.push({ role: "user", content: prompt });
    const res = await fetch(`${this.baseUrl}/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: model || this.model,
        messages,
        temperature,
        max_tokens: maxTokens,
      }),
    });
    if (!res.ok) throw new Error(`LM Studio error ${res.status}: ${await res.text()}`);
    const data = await res.json();
    return {
      text: data.choices?.[0]?.message?.content || "",
      model: model || this.model,
      provider: "lmstudio",
      latency_ms: Date.now() - started,
    };
  }
}

module.exports = { LMStudioProvider };
