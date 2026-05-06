from __future__ import annotations

from textual.widget import Widget
from textual.widgets import Static

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
        self.refresh()

    def compose(self):
        if self._result is None:
            yield Static("No results yet")
            return

        answer_text = self._result.answer[:200] + "..." if len(self._result.answer) > 200 else self._result.answer
        yield Static(f"Answer: {answer_text}", id="answer-text")
        yield Static(f"Grounded: {'✓' if self._result.is_grounded else '✗'}  "
                    f"Relevant: {'✓' if self._result.is_relevant else '✗'}",
                    id="critic-verdict")
        yield Static(f"Sources: {self._result.sources_count}", id="sources-count")
        yield Static(f"Comment: {self._result.comment}", id="critic-comment")
