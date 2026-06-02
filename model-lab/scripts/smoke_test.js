#!/usr/bin/env node
/** Provider smoke test — fails gracefully if Ollama/local provider unavailable. */
const { getProvider } = require("../src/providers/provider_router");

async function main() {
  const providerName = process.env.MODEL_PROVIDER || "ollama";
  console.log(`Model Lab smoke test — provider: ${providerName}`);

  let provider;
  try {
    provider = getProvider(providerName);
  } catch (e) {
    console.log("SMOKE SKIP:", e.message);
    console.log("Set MODEL_PROVIDER=ollama|lmstudio|openai|anthropic and configure env per model-lab/docs/provider_setup.md");
    process.exit(0);
  }

  const health = await provider.healthCheck();
  console.log("Health:", health);
  if (!health.ok) {
    console.log("\nProvider unavailable — this is OK for CI/build.");
    console.log("To fix Ollama: install from https://ollama.com, run `ollama serve`, then `npm run model:pull`");
    process.exit(0);
  }

  try {
    const res = await provider.generate({
      prompt: "Reply with one sentence: Bowers Frontier Macro Labs Model Lab smoke test OK.",
      system: "Be concise.",
      maxTokens: 60,
    });
    console.log("\nSample output:", res.text.trim());
    console.log(JSON.stringify({ provider: res.provider, model: res.model, latency_ms: res.latency_ms }, null, 2));
    console.log("model:smoke PASS");
  } catch (e) {
    console.log("SMOKE WARN:", e.message);
    process.exit(0);
  }
}

main();
