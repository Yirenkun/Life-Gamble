from __future__ import annotations
import os
import re
from typing import Any
import httpx

ESPORTS = ('esports','esport','lol','league of legends','cs2','counter strike','valorant','dota','dota 2','rocket league','rainbow six','r6','overwatch')
POLITICS = ('politic','election','president','presidential','senate','house','governor','congress','approval','referendum','party','democrat','republican','trump','biden')

class LiveMarketData:
    def __init__(self):
        self.base_url = os.getenv('PREDICT_BASE_URL','https://api.predict.fun').rstrip('/')
        self.api_key = os.getenv('PREDICT_API_KEY','')
        self.timeout = float(os.getenv('PREDICT_TIMEOUT','15'))

    def _headers(self):
        return {'x-api-key': self.api_key} if self.api_key else {}

    async def get(self, path: str, params: dict[str, Any] | None = None):
        async with httpx.AsyncClient(timeout=self.timeout) as c:
            r = await c.get(self.base_url + path, params=params, headers=self._headers())
            r.raise_for_status()
            return r.json()

    async def markets(self, limit: int = 100):
        return await self.get('/v1/markets', {'first': limit, 'status': 'OPEN'})

    async def orderbook(self, market_id: str):
        return await self.get(f'/v1/markets/{market_id}/orderbook')

    @staticmethod
    def unwrap(payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list): return payload
        if not isinstance(payload, dict): return []
        data = payload.get('data', payload)
        if isinstance(data, list): return data
        for k in ('markets','items','results','nodes'):
            if isinstance(data, dict) and isinstance(data.get(k), list): return data[k]
        return []

    @staticmethod
    def classify(m: dict[str, Any]) -> str:
        text = ' '.join(str(m.get(k,'')) for k in ('title','question','description','category','slug','tags')).lower()
        text = re.sub(r'[^a-z0-9 ]+', ' ', text)
        if any(x in text for x in ESPORTS): return 'Esports'
        if any(x in text for x in POLITICS): return 'Politics'
        return 'Other'

    @staticmethod
    def market_id(m: dict[str, Any]):
        return m.get('id') or m.get('marketId') or m.get('market_id')

    @staticmethod
    def title(m: dict[str, Any]):
        return m.get('title') or m.get('question') or m.get('name') or f"Market {LiveMarketData.market_id(m)}"

    async def categorized_markets(self, limit: int = 500):
        payload = await self.markets(limit)
        out=[]
        for m in self.unwrap(payload):
            category=self.classify(m)
            if category in ('Esports','Politics'):
                out.append({'id':self.market_id(m),'title':self.title(m),'category':category,'raw':m})
        return out
