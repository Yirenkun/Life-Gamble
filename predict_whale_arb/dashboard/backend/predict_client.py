import os
from typing import Any
import httpx

class PredictClient:
    def __init__(self, base_url: str = 'https://api.predict.fun', api_key: str | None = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv('PREDICT_API_KEY', '')

    async def _get(self, path: str, params: dict[str, Any] | None = None):
        headers = {'x-api-key': self.api_key} if self.api_key else {}
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(f'{self.base_url}{path}', params=params, headers=headers)
            r.raise_for_status()
            return r.json()

    async def markets(self, limit: int = 100):
        return await self._get('/v1/markets', {'first': limit, 'status': 'OPEN'})

    async def market(self, market_id: str):
        return await self._get(f'/v1/markets/{market_id}')

    async def orderbook(self, market_id: str):
        return await self._get(f'/v1/markets/{market_id}/orderbook')
