const { OllamaProvider } = require("./ollama_provider");
const { LMStudioProvider } = require("./lmstudio_provider");
const { OpenAIProvider } = require("./openai_provider");
const { AnthropicProvider } = require("./anthropic_provider");

function getProvider(name) {
  const provider = (name || process.env.MODEL_PROVIDER || "ollama").toLowerCase();
  switch (provider) {
    case "ollama":
      return new OllamaProvider({});
    case "lmstudio":
      return new LMStudioProvider({});
    case "openai":
      return new OpenAIProvider({});
    case "anthropic":
      return new AnthropicProvider({});
    default:
      throw new Error(`Unknown MODEL_PROVIDER: ${provider}`);
  }
}

module.exports = { getProvider };
