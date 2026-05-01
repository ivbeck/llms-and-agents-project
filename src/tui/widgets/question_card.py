from __future__ import annotations
from textual.widget import Widget
from src.tui.state import QuestionState, StepState

class QuestionCard(Widget):
    def __init__(self, state: QuestionState, **kwargs) -> None:
        super().__init__(**kwargs)
        self._state = state

    @property
    def question(self) -> str:
        return self._state.question

    @property
    def steps(self) -> list[StepState]:
        return self._state.steps