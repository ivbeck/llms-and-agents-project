from src.tui.widgets.question_card import QuestionCard
from src.tui.state import QuestionState, StepState

def test_question_card_binds_state():
    qs = QuestionState(id="q1", question="What is AI?", steps=[StepState(name="QueryPlanning")])
    card = QuestionCard(qs)
    assert card.question == "What is AI?"
    assert len(card.steps) == 1