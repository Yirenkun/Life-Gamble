# Predict Whale & Arbitrage Engine

A Python 3.11+ research/trading engine for Predict.fun focused on **Esports + Politics whale discovery, copy-trading signals, and arbitrage scanning**.

## Modes

- `paper`: default. Never sends an order.
- `live`: requires explicit `LIVE_TRADING=true` and a configured execution adapter.

## Core modules

- `predict_client.py` — Predict.fun REST client + orderbook access.
- `whale.py` — wallet scoring and category-specific filtering.
- `copy.py` — copy-trade decision engine with caps, cooldowns and circuit breakers.
- `arb.py` — cross-venue and structural arbitrage calculations.
- `service.py` — polling loop and JSONL event output.
- `config.py` — environment configuration.

## Strategy philosophy

A high win-rate wallet is not automatically a good wallet to follow. The scorer uses sample size, ROI, realized PnL, drawdown, category specialization, concentration, and recent consistency. Esports and Politics are scored independently.

## Setup

```bash
cd predict_whale_arb
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
python -m predict_whale_arb.service
```

For Linux/macOS replace `copy` with `cp`.

## API

Predict mainnet requires an API key. The official API exposes markets, orderbooks, positions by address, orders, and WebSocket market streams. See https://dev.predict.fun/.

### Environment

```text
PREDICT_API_KEY=
PREDICT_BASE_URL=https://api.predict.fun
WATCH_WALLETS=0xabc...,0xdef...
CATEGORY_ALLOWLIST=esports,politics
POLL_SECONDS=15
PAPER_TRADING=true
LIVE_TRADING=false
MAX_COPY_USD=50
MAX_WALLET_EXPOSURE_USD=250
MAX_DAILY_LOSS_USD=100
MIN_WHALE_SCORE=70
MIN_SAMPLE_TRADES=30
ARB_MIN_NET_EDGE=0.008
```

## Important

This repository intentionally ships with **paper trading as the safe default**. Live execution is separated behind an adapter and should only be enabled after backtesting and manual verification of market matching, fees, liquidity, and resolution rules.
