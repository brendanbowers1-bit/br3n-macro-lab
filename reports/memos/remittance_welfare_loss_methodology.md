# Remittance Welfare Loss Index — Methodology

## Definition
Estimates purchasing power lost between sender and recipient.

## Formula
welfare_loss_pct = 1 - real_value_delivered / gross_sent_usd
aggregate_welfare_loss_usd = remittance_usd × welfare_loss_pct

## Limitations
- Flow data may be lagged; corridor weights approximate
- Cash-out frictions use default assumptions
