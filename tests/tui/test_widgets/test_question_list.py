from src.tui.widgets.question_list import QuestionList
from src.tui.state import QuestionState

def test_question_list_initial():
    ql = QuestionList()
    assert len(ql.items) == 0

def test_question_list_add():
    ql = QuestionList()
    state = QuestionState(id="q1", question="What is x?")
    ql.add(state)
    assert len(ql.items) == 1
    assert ql.items[0].id == "q1"

def test_question_list_remove():
    ql = QuestionList()
    state = QuestionState(id="q1", question="What is x?")
    ql.add(state)
    assert len(ql.items) == 1
    ql.remove("q1")
    assert len(ql.items) == 0
