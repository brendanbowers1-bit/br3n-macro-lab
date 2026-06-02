const { BaseProvider } = require("./base_provider");

class OpenAIProvider extends BaseProvider {
  constructor(config) {
    super(config);
    this.apiKey = config.apiKey || process.env.OPENAI_API_KEY;
    this.model = config.model || process.env.MODEL_NAME || "gpt-4o-mini";
  }

  async healthCheck() {
    if (!this.apiKey) return { ok: false, message: "OPENAI_API_KEY not set" };
    return { ok: true, message: "OpenAI API key present" };
  }

  async generate({ prompt, system, model, temperature = 0.2, maxTokens = 1024 }) {
    if (!this.apiKey) throw new Error("OPENAI_API_KEY not set");
    const started = Date.now();
    const messages = [];
    if (system) messages.push({ role: "system", content: system });
    messages.push({ role: "user", content: prompt });
    const res = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model: model || this.model,
        messages,
        temperature,
        max_tokens: maxTokens,
      }),
    });
    if (!res.ok) throw new Error(`OpenAI error ${res.status}: ${await res.text()}`);
    const data = await res.json();
    return {
      text: data.choices?.[0]?.message?.content || "",
      model: model || this.model,
      provider: "openai",
      latency_ms: Date.now() - started,
    };
  }
}

module.exports = { OpenAIProvider };
