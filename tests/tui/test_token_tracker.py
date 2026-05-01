from src.tui.token_tracker import TokenTracker

def test_token_tracker_initialization():
    tracker = TokenTracker()
    assert tracker.tokens_in == 0
    assert tracker.tokens_out == 0
    assert tracker.tokens_reasoning == 0

def test_token_tracker_track():
    tracker = TokenTracker()
    tracker.track(100, 40, 10)
    assert tracker.tokens_in == 100
    assert tracker.tokens_out == 40
    assert tracker.tokens_reasoning == 10
    tracker.track(50, 20, 5)
    assert tracker.tokens_in == 150
    assert tracker.tokens_out == 60
    assert tracker.tokens_reasoning == 15

def test_token_tracker_reset():
    tracker = TokenTracker()
    tracker.tokens_in = 100
    tracker.tokens_out = 50
    tracker.tokens_reasoning = 20
    tracker.reset()
    assert tracker.tokens_in == 0
    assert tracker.tokens_out == 0
    assert tracker.tokens_reasoning == 0