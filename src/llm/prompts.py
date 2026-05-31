"""Prompt templates for FX research LLM tasks."""

TRADE_MEMO_PROMPT = """You are a senior FX strategist at an institutional research desk.
Write a professional FX trade memo. Be skeptical, precise, and research-oriented.
Do NOT promise returns or claim certainty.

Data:
Pair: {pair}
Direction: {direction}
Horizon: {horizon} days
Model: {model_name}
Probability up: {probability_up:.2%}
Expected return: {expected_return:.4f}
Confidence: {confidence:.2%}
Regime: {regime} ({regime_description})
Carry score: {carry_score}
Momentum 20d: {ret_20d:.2%}
Volatility 20d: {vol_20d:.2%}
Stop loss: {stop_loss:.5f}
Take profit: {take_profit:.5f}
Reward/risk: {reward_risk:.2f}
Risk decision: {trade_decision}

Format the memo with these sections:
- Pair
- Direction
- Time horizon
- Thesis
- Model signal
- Macro drivers
- Carry/rate explanation
- Technical/momentum confirmation
- Risk/reward
- Stop loss
- Take profit
- Invalidation conditions
- Event risks
- Confidence
- Final decision: trade / watchlist / avoid
"""

CENTRAL_BANK_TONE_PROMPT = """Classify the following central bank statement excerpt for FX research.

Text:
{text}

Respond in JSON-like structure:
- tone: hawkish / neutral / dovish
- confidence: 0-1
- key_phrases: list
- likely_fx_impact: brief
- risks_to_interpretation: brief
"""

NEWS_EVENT_PROMPT = """Classify this FX news headline for research purposes.

Headline:
{text}

Respond with:
- affected_currencies: list
- event_category: e.g. central_bank, geopolitical, inflation, growth
- risk_on_off: risk-on / risk-off / neutral
- expected_short_term_fx_direction: brief
- confidence: 0-1
- explanation: brief
"""

MODEL_SANITY_CHECK_PROMPT = """You are a quantitative FX researcher reviewing a model signal.

Pair: {pair}
Signal: {signal}
Probability up: {probability_up}
Top features: {features}

Answer:
1. Is the signal economically reasonable?
2. Which features support it?
3. Which features contradict it?
4. What could make the model wrong?
5. Is this likely overfit?
Be concise and skeptical.
"""
