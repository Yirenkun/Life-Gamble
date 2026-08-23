from __future__ import annotations

from dataclasses import dataclass
import time

from .whale import WhaleStats, Trade

@dataclass
class CopySignal:
    wallet: str
    market_id: int
    side: str
    source_price: float
    amount_usd: float
    category: str
    reason: str

class CopyEngine:
    def __init__(self, min_score: float, max_copy_usd: float, max_wallet_exposure_usd: float, max_daily_loss_usd: float):
        self.min_score = min_score
        self.max_copy_usd = max_copy_usd
        self.max_wallet_exposure_usd = max_wallet_exposure_usd
        self.max_daily_loss_usd = max_daily_loss_usd
        self.wallet_exposure: dict[str, float] = {}
        self.daily_pnl = 0.0
        self.last_signal: dict[tuple[str, int], float] = {}

    def signal(self, stats: WhaleStats, trade: Trade, now: float | None = None) -> CopySignal | None:
        now = now or time.time()
        if stats.score < self.min_score or trade.category not in {'esports', 'politics'}:
            return None
        if self.daily_pnl <= -self.max_daily_loss_usd:
            return None
        key = (trade.wallet.lower(), trade.market_id)
        if now - self.last_signal.get(key, 0) < 5:
            return None
        current = self.wallet_exposure.get(trade.wallet.lower(), 0.0)
        room = max(0.0, self.max_wallet_exposure_usd - current)
        amount = min(self.max_copy_usd, room)
        if amount <= 0:
            return None
        self.last_signal[key] = now
        self.wallet_exposure[trade.wallet.lower()] = current + amount
        return CopySignal(trade.wallet, trade.market_id, trade.side, trade.price, amount, trade.category, f'whale_score={stats.score:.1f}; roi={stats.roi:.2%}; win={stats.overall_win_rate:.1%}')
