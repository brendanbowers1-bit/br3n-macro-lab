const fs = require("fs");
const path = require("path");
const { getProvider } = require("../providers/provider_router");
const { SimpleVectorStore } = require("../rag/simple_vector_store");
const { ragContext } = require("../rag/rag_pipeline");
const { deterministicBrief } = require("./brief_templates");

async function generateCorridorBrief({ modelPath, validationPath, vectorStorePath, outMd, outJson }) {
  const model = JSON.parse(fs.readFileSync(modelPath, "utf8"));
  const validation = fs.existsSync(validationPath)
    ? JSON.parse(fs.readFileSync(validationPath, "utf8"))
    : null;
  const store = SimpleVectorStore.load(vectorStorePath);
  const rag = ragContext("USD/MXN corridor risk volatility settlement", store, 3);

  let providerName = "deterministic_fallback";
  let modelName = "transparent_models_v1";
  let llmText = null;
  let llmError = null;

  try {
    const provider = getProvider(process.env.MODEL_PROVIDER);
    const health = await provider.healthCheck();
    if (health.ok) {
      const prompt = `Write a concise research brief section (3 bullets max) summarizing corridor risk for treasury researchers.
Data mode: ${model.data_mode}. Score: ${model.corridor_risk_score.score}. Do NOT claim live data if synthetic. Do NOT recommend trades.`;
      const system =
        "You are Bowers Frontier Macro Labs research assistant. Research only. Not financial advice.";
      const res = await provider.generate({ prompt, system, maxTokens: 400 });
      llmText = res.text;
      providerName = res.provider;
      modelName = res.model;
    } else {
      llmError = health.message;
    }
  } catch (e) {
    llmError = e.message;
  }

  const markdown = deterministicBrief({ model, validation, rag });
  const finalMd =
    llmText && !llmError
      ? markdown.replace(
          "## Executive Summary",
          `## Executive Summary\n\n_LLM supplement (${providerName}/${modelName})_: ${llmText.trim()}\n`
        )
      : markdown;

  fs.mkdirSync(path.dirname(outMd), { recursive: true });
  fs.writeFileSync(outMd, finalMd);

  const payload = {
    lab: "Bowers Frontier Macro Labs",
    corridor: "USD/MXN",
    as_of: model.as_of,
    data_mode: model.data_mode,
    provider: providerName,
    model: modelName,
    validation_status: validation?.status || model.validation_status,
    corridor_risk_score: model.corridor_risk_score,
    carry_signal: model.carry_signal,
    llm_error: llmError,
    rag_sources: (rag.chunks || []).map((c) => c.source),
    generated_at: new Date().toISOString(),
    disclaimer: "Research only. Not financial advice.",
  };
  fs.writeFileSync(outJson, JSON.stringify(payload, null, 2));

  return { providerName, modelName, llmError };
}

module.exports = { generateCorridorBrief };
