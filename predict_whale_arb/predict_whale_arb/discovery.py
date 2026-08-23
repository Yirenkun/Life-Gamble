from __future__ import annotations

import re
import httpx

WALLET_RE = re.compile(r'Wallet:\s*`(0x[a-fA-F0-9]{40})`', re.I)

class PredictFunScanDiscovery:
    """Optional public discovery adapter.

    Predict.fun's official API exposes positions by address, but not a public
    arbitrary-wallet historical activity endpoint. This adapter uses the public
    PredictFunScan leaderboard pages to seed candidate wallets; all candidates
    should then be re-validated before copying.
    """
    def __init__(self, base_url: str = 'https://predictfunscan.com'):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client(timeout=20)

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

    def close(self) -> None:
        self.client.close()
