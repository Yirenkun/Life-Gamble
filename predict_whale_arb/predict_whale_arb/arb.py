from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re

@dataclass
class ArbOpportunity:
    market_id: int | str
    title: str
    yes_price: float
    external_yes_price: float
    edge: float
    net_edge: float
    direction: str
    confidence: float


def structural_binary_edge(yes_bid: float, yes_ask: float, fee_rate: float = 0.0) -> float:
    """Returns the executable edge for a binary YES/NO basket.

    Predict's orderbook is quoted on YES. Buying NO is economically equivalent
    to selling YES at the bid, so a same-book YES+NO basket is only a true arb
    if the venue exposes executable prices that cross after fees. This function
    therefore intentionally returns <= 0 for a normal crossed-free book.
    """
    if yes_bid is None or yes_ask is None:
        return 0.0
    gross = 1.0 - (yes_ask + (1.0 - yes_bid))
    return gross - fee_rate * 2


def cross_venue_edge(predict_yes: float, external_yes: float, fee_predict: float = 0.0, fee_external: float = 0.0) -> ArbOpportunity | None:
    """Find a two-leg price dislocation for the same binary question.

    The caller must separately validate that both markets have identical
    resolution criteria and that both legs are independently executable.
    """
    buy_predict_sell_external = external_yes - predict_yes - fee_predict - fee_external
    buy_external_sell_predict = predict_yes - external_yes - fee_predict - fee_external
    if buy_predict_sell_external <= 0 and buy_external_sell_predict <= 0:
        return None
    if buy_predict_sell_external >= buy_external_sell_predict:
        edge = buy_predict_sell_external
        direction = 'BUY_PREDICT_YES_SELL_EXTERNAL_YES'
    else:
        edge = buy_external_sell_predict
        direction = 'BUY_EXTERNAL_YES_SELL_PREDICT_YES'
    return ArbOpportunity('', '', predict_yes, external_yes, edge, edge, direction, min(1.0, edge / 0.05))


def normalize_title(title: str) -> str:
    s = title.lower()
    s = re.sub(r'[^a-z0-9 ]+', ' ', s)
    s = re.sub(r'\b(will|be|the|a|an|to|of|on|in|this|win|wins)\b', ' ', s)
    return ' '.join(s.split())


def fuzzy_match_score(a: str, b: str) -> float:
    aa, bb = set(normalize_title(a).split()), set(normalize_title(b).split())
    if not aa or not bb:
        return 0.0
    return len(aa & bb) / len(aa | bb)
