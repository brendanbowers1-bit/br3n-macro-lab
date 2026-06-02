const questions = require("./eval_questions");
const schema = require("./scoring_schema");
const { getProvider } = require("../providers/provider_router");

async function runEvals({ modelRunPath }) {
  const fs = require("fs");
  const context = fs.existsSync(modelRunPath) ? JSON.parse(fs.readFileSync(modelRunPath, "utf8")) : {};

  let providerStatus = "unavailable";
  let providerName = process.env.MODEL_PROVIDER || "ollama";
  let results = [];

  try {
    const provider = getProvider(providerName);
    const health = await provider.healthCheck();
    if (health.ok) {
      providerStatus = "available";
      // Run a subset (5) live to avoid long CI; store methodology for rest
      const subset = questions.slice(0, 5);
      for (const q of subset) {
        const prompt = `${q.question}\n\nStructured context: data_mode=${context.data_mode}, CRS=${context.corridor_risk_score?.score}, validation=${context.validation_status}. Do not recommend trades.`;
        try {
          const res = await provider.generate({ prompt, system: "Bowers Frontier Macro Labs eval. Research only.", maxTokens: 300 });
          results.push({ ...q, answer: res.text, provider: res.provider, model: res.model, latency_ms: res.latency_ms, scored: false });
        } catch (e) {
          results.push({ ...q, error: e.message, scored: false });
        }
      }
    } else {
      providerStatus = `unavailable: ${health.message}`;
    }
  } catch (e) {
    providerStatus = `unavailable: ${e.message}`;
  }

  return {
    lab: "Bowers Frontier Macro Labs",
    question_count: questions.length,
    questions_run_live: results.length,
    provider: providerName,
    provider_status: providerStatus,
    scoring_schema: schema,
    results,
    pending_questions: questions.slice(results.length),
    note: "Full 25-question battery defined; run live when provider available. No comparative 'beats Claude' claims without stored benchmarks.",
    generated_at: new Date().toISOString(),
  };
}

module.exports = { runEvals };
