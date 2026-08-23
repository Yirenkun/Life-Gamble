from __future__ import annotations

import re
from dataclasses import dataclass
import httpx

PROFILE_RE = re.compile(r'on Predict\.Fun:\s*([+-]?\$[\d,]+(?:\.\d+)?) all-time PnL,\s*([\d,]+) trades,\s*([\d.]+)% win rate,\s*\$([\d,]+(?:\.\d+)?) volume', re.I)
WALLET_RE = re.compile(r'Wallet:\s*`(0x[a-fA-F0-9]{40})`', re.I)

@dataclass
class WhaleProfile:
    wallet: str
    pnl_usd: float
    trades: int
    win_rate: float
    volume_usd: float

    @property
    def roi(self) -> float:
        return self.pnl_usd / self.volume_usd if self.volume_usd else 0.0

    @property
    def score(self) -> float:
        sample = min(1.0, self.trades / 500)
        wr = max(0.0, min(1.0, (self.win_rate - 50.0) / 20.0))
        roi = max(0.0, min(1.0, self.roi / 0.05))
        pnl = min(1.0, max(0.0, self.pnl_usd) / 100_000)
        return 100 * (0.35 * wr + 0.25 * roi + 0.20 * sample + 0.20 * pnl)

class PredictFunScanDiscovery:
    """Optional public discovery adapter used to seed candidate wallets."""
    def __init__(self, base_url: str = 'https://predictfunscan.com'):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client(timeout=20, follow_redirects=True)

    def top_wallets(self, limit: int = 50) -> list[str]:
        html = self.client.get(self.base_url + '/').text
        seen: list[str] = []
        for wallet in WALLET_RE.findall(html):
            w = wallet.lower()
            if w not in seen:
                seen.append(w)
            if len(seen) >= limit:
                break
        return seen

    def profile(self, wallet: str) -> WhaleProfile | None:
        html = self.client.get(f'{self.base_url}/pf/address/{wallet}').text
        m = PROFILE_RE.search(re.sub(r'\s+', ' ', html))
        if not m:
            return None
        def money(x: str) -> float:
            return float(x.replace('$', '').replace(',', ''))
        return WhaleProfile(wallet.lower(), money(m.group(1)), int(m.group(2).replace(',', '')), float(m.group(3)), money(m.group(4)))

    def discover(self, limit: int = 50, min_score: float = 50.0) -> list[WhaleProfile]:
        profiles = []
        for wallet in self.top_wallets(limit):
            try:
                p = self.profile(wallet)
                if p and p.score >= min_score:
                    profiles.append(p)
            except httpx.HTTPError:
                continue
        return sorted(profiles, key=lambda p: p.score, reverse=True)

    def close(self) -> None:
        self.client.close()
