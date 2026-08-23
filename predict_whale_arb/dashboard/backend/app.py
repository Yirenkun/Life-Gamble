from __future__ import annotations
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from .market_data import LiveMarketData

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / 'dashboard' / 'frontend' / 'index.html'
app = FastAPI(title='Predict Whale Hunter', version='1.1.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
MODE='paper'
WATCHLIST: list[str]=[]
DEMO_WHALES=[{'wallet':'0x8ad2…fc25','category':'Esports','specialty':'LoL','win_rate':76.4,'roi':41.2,'pnl':184221,'score':94},{'wallet':'0x4fad…0e85','category':'Politics','specialty':'Election','win_rate':69.8,'roi':37.0,'pnl':92300,'score':91},{'wallet':'0x04b6…cdae','category':'Esports','specialty':'CS2','win_rate':71.8,'roi':35.7,'pnl':56300,'score':89}]
DEMO_ARB=[{'event':'Live feed ready — no executable opportunity yet','venue_a':'Predict.fun','venue_b':'Polymarket','net_edge':0.0,'confidence':0.0,'status':'waiting'}]
class ModeRequest(BaseModel): mode:str
class WalletRequest(BaseModel): wallet:str=Field(min_length=10)

def demo_enabled(): return os.getenv('DEMO_MODE','true').lower()=='true'

def configured(): return bool(os.getenv('PREDICT_API_KEY'))

@app.get('/')
def index(): return FileResponse(FRONTEND)
@app.get('/api/health')
def health(): return {'status':'ok','mode':MODE,'live_enabled':False,'predict_configured':configured(),'demo':demo_enabled()}
@app.get('/api/dashboard')
def dashboard():
 return {'mode':MODE,'live_enabled':False,'demo':demo_enabled(),'predict_configured':configured(),'account':{'balance':0,'today_pnl':0,'copy_pnl':0,'arb_pnl':0},'whales':{'total':len(DEMO_WHALES) if demo_enabled() else len(WATCHLIST),'esports':2 if demo_enabled() else 0,'politics':1 if demo_enabled() else 0},'signals':{'copy':0,'arbitrage':0},'message':'Demo data is shown until Predict.fun credentials are configured.' if demo_enabled() else 'Predict.fun market connection is active.'}
@app.get('/api/whales')
async def whales():
 if demo_enabled(): return {'items':DEMO_WHALES,'source':'demo'}
 return {'items':[],'source':'predict.fun','note':'Historical whale index worker is the next live-data stage.'}
@app.get('/api/markets')
async def markets():
 if not configured(): return {'items':[],'configured':False}
 try: return {'items':await LiveMarketData().categorized_markets(int(os.getenv('MARKET_LIMIT','500'))),'configured':True}
 except Exception as e: raise HTTPException(502,f'Predict.fun market feed unavailable: {e}')
@app.get('/api/market/{market_id}/orderbook')
async def orderbook(market_id:str):
 if not configured(): raise HTTPException(400,'Predict.fun API key is not configured')
 try: return await LiveMarketData().orderbook(market_id)
 except Exception as e: raise HTTPException(502,f'Orderbook unavailable: {e}')
@app.get('/api/arbitrage')
async def arbitrage():
 if demo_enabled(): return {'items':DEMO_ARB,'source':'demo'}
 return {'items':[],'source':'live','note':'Cross-venue matcher will only emit validated executable pairs.'}
@app.get('/api/settings')
def settings(): return {'mode':MODE,'paper_trading':True,'live_trading':False,'predict_configured':configured(),'max_copy_usd':float(os.getenv('MAX_COPY_USD','50')),'max_wallet_exposure_usd':float(os.getenv('MAX_WALLET_EXPOSURE_USD','250')),'max_daily_loss_usd':float(os.getenv('MAX_DAILY_LOSS_USD','100')),'min_whale_score':float(os.getenv('MIN_WHALE_SCORE','70')),'min_sample_trades':int(os.getenv('MIN_SAMPLE_TRADES','30')),'arb_min_net_edge':float(os.getenv('ARB_MIN_NET_EDGE','0.008'))}
@app.post('/api/mode')
def set_mode(req:ModeRequest):
 global MODE
 if req.mode not in ('paper','live'): raise HTTPException(400,'mode must be paper or live')
 if req.mode=='live': raise HTTPException(403,'Live mode is locked until credentials, execution and safety checks are verified.')
 MODE='paper'; return {'ok':True,'mode':MODE}
@app.post('/api/wallets')
def add_wallet(req:WalletRequest):
 wallet=req.wallet.strip().lower()
 if wallet not in WATCHLIST: WATCHLIST.append(wallet)
 return {'ok':True,'wallets':WATCHLIST}
