# Open Source FX AI Model Lab — Benchmark Standard

Every open-source model benchmarked in Bowers Frontier Macro Labs must use:

- Same currency pair
- Same timeframe
- Same train/test split (pre-registered)
- Same transaction cost assumptions
- Same evaluation dates
- Same risk limits
- Same walk-forward testing method

## Metrics

- directional accuracy
- precision on trade signals
- recall on trade signals
- Sharpe ratio
- Sortino ratio
- max drawdown
- average win / average loss
- win rate
- profit factor
- turnover
- transaction cost drag
- performance by regime

## Warning

These models are not trading systems by themselves. They are research baselines. Every model must be tested out-of-sample with realistic transaction costs, drawdown controls, and no look-ahead bias before any trading use.
