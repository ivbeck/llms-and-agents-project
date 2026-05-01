from src.tui.state import QuestionState, StepState

def test_question_state_defaults():
    qs = QuestionState(id="q1", question="What is x?")
    assert qs.status == "pending"
    assert qs.steps == []
    assert qs.logs == []
    assert qs.tokens_in == 0
    assert qs.tokens_out == 0
    assert qs.tokens_reasoning == 0
    assert qs.result is None
    assert qs.error is None

def test_step_state_defaults():
    ss = StepState(name="QueryPlanning")
    assert ss.status == "pending"
    assert ss.tokens_in == 0
    assert ss.tokens_out == 0
    assert ss.tokens_reasoning == 0
    assert ss.started_at is None
    assert ss.finished_at is None