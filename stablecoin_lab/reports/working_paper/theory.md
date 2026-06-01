# Theory (Draft)

## Settlement windows and trust relocation

When ledger confirmation approaches real time, residual trust must settle in:

1. **Issuer reserves** — liquidity, composition, redemption capacity
2. **Compliance infrastructure** — KYC/AML, sanctions screening, travel rule
3. **Off-ramp markets** — local FX, banking partners, corridor frictions
4. **Legal enforceability** — bankruptcy remoteness, redemption claims
5. **Secondary market depth** — arbitrage that enforces peg parity

## Propositions (measurement, not causal claims)

**P1.** Faster ledger finality does not imply higher economic finality without low compliance and off-ramp frictions.

**P2.** Settlement window compression may reduce working-capital cost while increasing run-speed fragility and issuer reserve burden.

**P3.** Multiple tokenized dollars may fragment singleness of money under stress unless redemption parity and reserve quality align.

**P4.** Stablecoin remittance advantage is corridor-specific and friction-dependent — not universal.

These propositions map to hypotheses H1–H5 in `src/research/hypotheses.py`.
