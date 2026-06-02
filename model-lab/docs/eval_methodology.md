# Eval Methodology

25 questions in `model-lab/src/evals/eval_questions.js` covering FX, carry, settlement, remittance, stablecoins, data limitations, and financial safety.

## Scoring (0–5 each)

- factuality
- domain_specificity
- data_grounding
- uncertainty_handling
- actionability
- hallucination_risk_control
- financial_safety

Live runs execute a subset when a provider is available; full battery stored for manual or CI expansion.

**No comparative "beats Claude/OpenAI" claims** without stored benchmark runs.

Run: `npm run model:eval`
