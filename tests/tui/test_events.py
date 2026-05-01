from src.tui.events import QuestionStateChanged, TokenAccumulated, LogAppended

def test_question_state_changed():
    evt = QuestionStateChanged(question_id="q1", status="running", current_step="HyDE Gen")
    assert evt.question_id == "q1"
    assert evt.status == "running"
    assert evt.current_step == "HyDE Gen"

def test_token_accumulated():
    evt = TokenAccumulated(question_id="q1", step_name="QueryPlanning", tokens_in=100, tokens_out=40, tokens_reasoning=0)
    assert evt.question_id == "q1"
    assert evt.step_name == "QueryPlanning"
    assert evt.tokens_in == 100
    assert evt.tokens_out == 40
    assert evt.tokens_reasoning == 0

def test_log_appended():
    evt = LogAppended(question_id="q1", message="Search completed")
    assert evt.question_id == "q1"
    assert evt.message == "Search completed"