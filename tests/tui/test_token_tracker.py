from src.tui.token_tracker import TokenTracker

def test_token_tracker_initialization():
    tracker = TokenTracker()
    assert tracker.tokens_in == 0
    assert tracker.tokens_out == 0
    assert tracker.tokens_reasoning == 0

def test_token_tracker_reset():
    tracker = TokenTracker()
    tracker.tokens_in = 100
    tracker.tokens_out = 50
    tracker.tokens_reasoning = 20
    tracker.reset()
    assert tracker.tokens_in == 0
    assert tracker.tokens_out == 0
    assert tracker.tokens_reasoning == 0