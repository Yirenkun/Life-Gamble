# Predict Whale & Arbitrage Engine

A Python 3.11+ research/trading engine for Predict.fun focused on **Esports + Politics whale discovery, copy-trading signals, and cross-venue arbitrage scanning**.

## What this build does

- Discovers candidate wallets from a public Predict.Fun analytics leaderboard adapter.
- Scores candidate whales using lifetime PnL, volume, sample size and win rate.
- Uses Predict.fun positions to identify current **Esports / Politics** exposure.
- Emits copy-trading signals with per-wallet caps, cooldowns and a daily-loss circuit breaker.
- Scans Predict.fun against Polymarket for likely cross-venue price dislocations.
- Keeps execution in `paper` mode by default; live order submission is intentionally isolated.

## Important data limitation

Predict.fun's public API provides positions by arbitrary address, but its account-activity endpoint is authenticated for the connected account. Therefore the discovery layer uses a public analytics/indexing source to seed wallets, while the official Predict API is used for market/orderbook/position data. Do **not** treat current positions as lifetime trade history.

## Setup

```bash
cd predict_whale_arb
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
```

For Linux/macOS replace `copy` with `cp`.

### Whale / copy scanner

```bash
python -m predict_whale_arb.service
```

Set `WATCH_WALLETS` for known wallets. If it is empty, use the discovery adapter separately or extend `service.py` to refresh the candidate list automatically.

### Cross-venue arbitrage scanner

```bash
python -m predict_whale_arb.arb_service
```

The scanner uses fuzzy matching only as a **candidate generator**. Before any real trade, exact question wording, resolution source, end time, outcome mapping, fees, depth and settlement mechanics must be verified.

## Environment

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
POLYMARKET_GAMMA_URL=https://gamma-api.polymarket.com
```

## Architecture

`discovery.py` → candidate wallets → `whale.py` → category/exposure analysis → `copy.py` → risk gate → `execution.py`.

For arbitrage: `Predict API + Polymarket Gamma` → `arb.py` → candidate match → fee/depth/resolution validation → paper signal.

The repository intentionally ships with **paper trading as the safe default**. Live execution should only be enabled after backtesting and manual verification of market matching, fees, liquidity, wallet permissions and resolution rules.
