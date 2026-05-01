from __future__ import annotations
from textual.widget import Widget
from src.tui.state import AnswerResult

class ResultsPanel(Widget):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._result: AnswerResult | None = None

    @property
    def answer(self) -> str:
        if self._result is None:
            return ""
        return self._result.answer

    @property
    def sources_count(self) -> int:
        if self._result is None:
            return 0
        return self._result.sources_count

    def bind_result(self, result: AnswerResult) -> None:
        self._result = result
