# Predict Whale Hunter Dashboard

Web control panel for the Predict.fun whale/copy/arbitrage engine.

## Current status

- Responsive browser UI
- Dashboard health endpoint
- Paper/live mode control (live intentionally locked)
- Whale and arbitrage API placeholders
- Safe default: paper trading

## Run locally

```bash
cd predict_whale_arb/dashboard/backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8080
```

Then open `http://127.0.0.1:8080` after placing the frontend behind a static server, or use the frontend file directly for UI preview.

## Next integration

The dashboard is intentionally separated from secrets and execution. The next integration wires the existing whale/arbitrage workers into the API and adds authentication, persistent storage, live market streams, backtest views, and a controlled execution adapter.
