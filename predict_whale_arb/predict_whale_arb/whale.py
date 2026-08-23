from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
import math

@dataclass
class Trade:
    wallet: str
    market_id: int
    title: str
    category: str
    side: str
    price: float
    amount_usd: float
    pnl_usd: float | None = None
    timestamp: float = 0.0

@dataclass
class WhaleStats:
    wallet: str
    trades: list[Trade] = field(default_factory=list)
    score: float = 0.0
    overall_win_rate: float = 0.0
    roi: float = 0.0
    realized_pnl: float = 0.0
    max_drawdown: float = 0.0
    esports_win_rate: float = 0.0
    politics_win_rate: float = 0.0
    esports_roi: float = 0.0
    politics_roi: float = 0.0


def classify_market(market: dict) -> str:
    text = ' '.join(str(market.get(k, '')) for k in ('title', 'question', 'categorySlug', 'marketType', 'marketVariant')).lower()
    variant = str((market.get('variantData') or {}).get('type', '')).lower()
    if 'esport' in text or 'esport' in variant or any(x in text for x in ('dota', 'lol', 'league of legends', 'valorant', 'cs2', 'counter-strike')):
        return 'esports'
    if 'polit' in text or any(x in text for x in ('election', 'president', 'senate', 'house race', 'approval rating')):
        return 'politics'
    return 'other'


def _drawdown(pnls: list[float]) -> float:
    peak = 0.0
    equity = 0.0
    worst = 0.0
    for pnl in pnls:
        equity += pnl
        peak = max(peak, equity)
        if peak > 0:
            worst = max(worst, (peak - equity) / peak)
    return worst


def score_whale(wallet: str, trades: list[Trade], min_sample: int = 30) -> WhaleStats:
    stats = WhaleStats(wallet=wallet, trades=trades)
    if not trades:
        return stats
    resolved = [t for t in trades if t.pnl_usd is not None]
    if not resolved:
        return stats
    wins = [t for t in resolved if t.pnl_usd > 0]
    invested = sum(max(t.amount_usd, 0) for t in resolved)
    pnl = sum(t.pnl_usd or 0 for t in resolved)
    stats.overall_win_rate = len(wins) / len(resolved)
    stats.realized_pnl = pnl
    stats.roi = pnl / invested if invested else 0.0
    stats.max_drawdown = _drawdown([t.pnl_usd or 0 for t in sorted(resolved, key=lambda x: x.timestamp)])

    for category in ('esports', 'politics'):
        sub = [t for t in resolved if t.category == category]
        if sub:
            sub_wins = sum(1 for t in sub if t.pnl_usd > 0)
            sub_invested = sum(max(t.amount_usd, 0) for t in sub)
            sub_pnl = sum(t.pnl_usd or 0 for t in sub)
            setattr(stats, f'{category}_win_rate', sub_wins / len(sub))
            setattr(stats, f'{category}_roi', sub_pnl / sub_invested if sub_invested else 0.0)

    sample_factor = min(1.0, len(resolved) / max(min_sample, 1))
    stability = max(0.0, 1.0 - stats.max_drawdown)
    roi_factor = min(1.0, max(0.0, stats.roi) / 0.50)
    win_factor = max(0.0, min(1.0, (stats.overall_win_rate - 0.50) / 0.30))
    specialist = max(stats.esports_roi, stats.politics_roi, 0.0)
    specialist_factor = min(1.0, specialist / 0.50)
    pnl_factor = min(1.0, max(0.0, math.log10(1 + max(stats.realized_pnl, 0)) / 5))
    stats.score = 100 * (0.25 * win_factor + 0.25 * roi_factor + 0.15 * stability + 0.15 * sample_factor + 0.10 * specialist_factor + 0.10 * pnl_factor)
    return stats
