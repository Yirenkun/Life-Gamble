from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title='Predict Whale Hunter Dashboard')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

MODE = 'paper'
WALLETS = []

class ModeRequest(BaseModel):
    mode: str

class WalletRequest(BaseModel):
    wallet: str

@app.get('/api/health')
def health():
    return {'status':'ok','time':datetime.utcnow().isoformat()+'Z','mode':MODE}

@app.get('/api/dashboard')
def dashboard():
    return {
        'mode': MODE,
        'account': {'balance': 0, 'today_pnl': 0, 'copy_pnl': 0, 'arb_pnl': 0},
        'whales': {'total': len(WALLETS), 'esports': 0, 'politics': 0},
        'signals': {'copy': 0, 'arbitrage': 0},
        'message': 'Connect Predict.fun credentials in your private runtime to enable live data.'
    }

@app.post('/api/mode')
def set_mode(req: ModeRequest):
    global MODE
    if req.mode not in ('paper','live'):
        return {'ok':False,'error':'mode must be paper or live'}
    if req.mode == 'live':
        return {'ok':False,'error':'Live mode is locked until execution credentials and safety checks are configured.'}
    MODE = req.mode
    return {'ok':True,'mode':MODE}

@app.post('/api/wallets')
def add_wallet(req: WalletRequest):
    wallet=req.wallet.strip().lower()
    if wallet and wallet not in WALLETS:
        WALLETS.append(wallet)
    return {'ok':True,'wallets':WALLETS}

@app.get('/api/whales')
def whales():
    return {'items':[], 'message':'Whale discovery worker will populate this view when Predict.fun data is connected.'}

@app.get('/api/arbitrage')
def arbitrage():
    return {'items':[], 'message':'Arbitrage scanner is running in paper-safe mode; no real orders are submitted.'}
