from src.tui.widgets.token_meter import TokenMeter

def test_token_meter_defaults():
    tm = TokenMeter()
    assert tm.tokens_in == 0
    assert tm.tokens_out == 0

def test_token_meter_update():
    tm = TokenMeter()
    tm.update(1200, 400, 0)
    assert tm.tokens_in == 1200
    assert tm.tokens_out == 400
    assert tm.tokens_reasoning == 0