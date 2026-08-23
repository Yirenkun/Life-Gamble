from __future__ import annotations

import json
import time
import httpx

from .arb import fuzzy_match_score, cross_venue_edge
from .config import Settings
from .predict_client import PredictClient


def _poly_price(m: dict) -> float | None:
    raw = m.get('outcomePrices') or m.get('outcome_prices')
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return None
    if isinstance(raw, list) and raw:
        try:
            return float(raw[0])
        except (TypeError, ValueError):
            return None
    outcomes = m.get('outcomes')
    if isinstance(outcomes, list) and outcomes:
        first = outcomes[0]
        if isinstance(first, dict):
            try:
                return float(first.get('price'))
            except (TypeError, ValueError):
                return None
    return None


def run() -> None:
    cfg = Settings()
    if not cfg.predict_api_key:
        raise SystemExit('PREDICT_API_KEY is required for arbitrage scanning')
    predict = PredictClient(cfg.predict_base_url, cfg.predict_api_key)
    poly = httpx.Client(timeout=20)
    try:
        while True:
            markets = predict.markets(first=100).get('data', [])
            try:
                pm = poly.get(f'{cfg.polymarket_gamma_url}/markets', params={'active': 'true', 'closed': 'false', 'limit': 1000}).json()
                pm_markets = pm.get('data', pm) if isinstance(pm, dict) else pm
            except Exception as exc:
                print(json.dumps({'type': 'arb_error', 'error': f'polymarket: {exc}'}))
                pm_markets = []
            for m in markets:
                title = str(m.get('title') or m.get('question') or '')
                if not title:
                    continue
                best = None
                best_score = 0.0
                for p in pm_markets:
                    pt = str(p.get('question') or p.get('title') or '')
                    score = fuzzy_match_score(title, pt)
                    if score > best_score:
                        best, best_score = p, score
                if not best or best_score < 0.72:
                    continue
                try:
                    book = predict.orderbook(int(m['id']))
                    _, predict_ask = predict.best_prices(book)
                    poly_yes = _poly_price(best)
                    if predict_ask is None or poly_yes is None:
                        continue
                    opp = cross_venue_edge(predict_ask, poly_yes)
                    if opp and opp.net_edge >= cfg.arb_min_net_edge:
                        opp.market_id = m['id']
                        opp.title = title
                        opp.confidence = best_score
                        print(json.dumps({'type': 'arb', 'opportunity': opp.__dict__}))
                except Exception as exc:
                    print(json.dumps({'type': 'arb_market_error', 'market_id': m.get('id'), 'error': str(exc)}))
            time.sleep(max(5, cfg.poll_seconds))
    finally:
        predict.close()
        poly.close()

if __name__ == '__main__':
    run()
