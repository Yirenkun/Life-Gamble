from __future__ import annotations

from dataclasses import dataclass

from .copy import CopySignal

@dataclass
class ExecutionResult:
    accepted: bool
    mode: str
    order_id: str | None
    reason: str

class PaperExecutor:
    def submit(self, signal: CopySignal) -> ExecutionResult:
        return ExecutionResult(True, 'paper', None, f'paper order: {signal.side} ${signal.amount_usd:.2f} market={signal.market_id}')

class LiveExecutor:
    """Live execution boundary.

    Keep this separate from signal generation. The official Predict SDK supports
    LIMIT/MARKET orders and account signing, but live execution should be wired
    only after credentials, allowances, market-resolution matching and a testnet
    run have been verified.
    """
    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def submit(self, signal: CopySignal) -> ExecutionResult:
        if not self.enabled:
            return ExecutionResult(False, 'live-disabled', None, 'LIVE_TRADING is disabled')
        raise RuntimeError('Live executor is intentionally not enabled in this build')
