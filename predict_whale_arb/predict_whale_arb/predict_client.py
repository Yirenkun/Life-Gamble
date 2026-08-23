from __future__ import annotations

from typing import Any
import httpx

class PredictClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 15.0):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client(timeout=timeout, headers={'x-api-key': api_key} if api_key else {})

    def close(self) -> None:
        self.client.close()

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        r = self.client.get(f'{self.base_url}{path}', params=params)
        r.raise_for_status()
        return r.json()

    def markets(self, first: int = 100, after: str | None = None, status: str = 'OPEN') -> dict[str, Any]:
        params = {'first': first, 'status': status}
        if after:
            params['after'] = after
        return self._get('/v1/markets', params)

    def orderbook(self, market_id: int) -> dict[str, Any]:
        return self._get(f'/v1/markets/{market_id}/orderbook')

    def positions_by_address(self, address: str, first: int = 100, after: str | None = None) -> dict[str, Any]:
        params = {'first': first}
        if after:
            params['after'] = after
        return self._get(f'/v1/positions/{address}', params)

    def orders(self, first: int = 100, after: str | None = None, market_id: int | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {'first': first}
        if after:
            params['after'] = after
        if market_id is not None:
            params['marketId'] = market_id
        return self._get('/v1/orders', params)

    @staticmethod
    def best_prices(book: dict[str, Any]) -> tuple[float | None, float | None]:
        data = book.get('data', book)
        bids = data.get('bids') or []
        asks = data.get('asks') or []
        bid = float(bids[0][0]) if bids else None
        ask = float(asks[0][0]) if asks else None
        return bid, ask
