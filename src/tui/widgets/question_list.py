from __future__ import annotations
from textual.widget import Widget
from src.tui.state import QuestionState

class QuestionList(Widget):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.items: list[QuestionState] = []

    def add(self, state: QuestionState) -> None:
        self.items.append(state)

    def remove(self, qid: str) -> None:
        self.items = [s for s in self.items if s.id != qid]
