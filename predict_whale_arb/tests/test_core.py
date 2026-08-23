from predict_whale_arb.arb import cross_venue_edge, fuzzy_match_score
from predict_whale_arb.whale import Trade, classify_market, score_whale


def test_cross_venue_edge():
    opp = cross_venue_edge(0.42, 0.47, 0.005, 0.005)
    assert opp is not None
    assert opp.net_edge > 0


def test_match_score():
    assert fuzzy_match_score('Will Team A win?', 'Will Team A win the match?') > 0.3


def test_esports_classification():
    assert classify_market({'title': 'Team A vs Team B - Dota 2'}) == 'esports'
    assert classify_market({'title': 'Who will win the presidential election?'}) == 'politics'


def test_whale_scoring():
    trades = [Trade('0x1', 1, 'test', 'esports', 'Yes', .5, 100, 20, i) for i in range(40)]
    stats = score_whale('0x1', trades, 30)
    assert stats.overall_win_rate == 1.0
    assert stats.esports_roi > 0
    assert stats.score > 0
