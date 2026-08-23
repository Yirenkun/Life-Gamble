from __future__ import annotations

import json
import time
from dataclasses import asdict

from .config import Settings
from .predict_client import PredictClient
from .copy import CopyEngine
from .whale import Trade, classify_market, score_whale


def _market_from_position(position: dict) -> dict:
    return position.get('market') or {}


def positions_to_trades(wallet: str, payload: dict) -> list[Trade]:
    out: list[Trade] = []
    for p in payload.get('data', []):
        market = _market_from_position(p)
        category = classify_market(market)
        if category not in {'esports', 'politics'}:
            continue
        try:
            amount = float(p.get('valueUsd') or 0)
            avg = float(p.get('averageBuyPriceUsd') or 0)
            pnl_raw = p.get('pnlUsd')
            pnl = float(pnl_raw) if pnl_raw is not None else None
        except (TypeError, ValueError):
            continue
        outcome = p.get('outcome') or {}
        side = str(outcome.get('name') or outcome.get('title') or 'Yes')
        out.append(Trade(wallet, int(market.get('id', 0)), str(market.get('title') or market.get('question') or ''), category, side, avg, amount, pnl))
    return out


def run() -> None:
    cfg = Settings()
    client = PredictClient(cfg.predict_base_url, cfg.predict_api_key)
    engine = CopyEngine(cfg.min_whale_score, cfg.max_copy_usd, cfg.max_wallet_exposure_usd, cfg.max_daily_loss_usd)
    print(json.dumps({'status': 'started', 'mode': 'paper' if cfg.paper_trading or not cfg.live_trading else 'live', 'categories': sorted(cfg.categories)}))
    try:
        while True:
            for wallet in cfg.wallets:
                try:
                    payload = client.positions_by_address(wallet)
                    trades = [t for t in positions_to_trades(wallet, payload) if t.category in cfg.categories]
                    stats = score_whale(wallet, trades, cfg.min_sample_trades)
                    print(json.dumps({'type': 'whale', **asdict(stats)}, default=str))
                    # Positions are used for current exposure monitoring. They are
                    # deliberately not treated as a lifetime trade history.
                    for trade in trades:
                        signal = engine.signal(stats, trade)
                        if signal:
                            print(json.dumps({'type': 'copy_signal', **asdict(signal)}))
                except Exception as exc:
                    print(json.dumps({'type': 'error', 'wallet': wallet, 'error': str(exc)}))
            time.sleep(max(1, cfg.poll_seconds))
    finally:
        client.close()

if __name__ == '__main__':
    run()
