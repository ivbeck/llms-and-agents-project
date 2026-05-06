from __future__ import annotations

from textual.widget import Widget
from textual.widgets import Static
from textual.reactive import reactive
from textual.events import Click

from src.tui.state import QuestionState


class QuestionList(Widget):
    selected_id: reactive[str | None] = reactive(None)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._states: list[QuestionState] = []

    def watch_selected_id(self, qid: str | None) -> None:
        self.refresh()

    def compose(self):
        if not self._states:
            yield Static("No questions yet. Press A to add.", id="empty-message")
            return

        for state in self._states:
            status_icon = self._status_icon(state.status)
            is_selected = state.id == self.selected_id
            yield Static(
                f"{status_icon} {state.question[:30]}",
                classes=f"question-item {'selected' if is_selected else ''}",
                id=f"q-{state.id}",
            )

    def _status_icon(self, status: str) -> str:
        return {"pending": "○", "running": "●", "done": "✓", "failed": "✗", "cancelled": "◌"}.get(status, "○")

    def on_click(self, event: Click) -> None:
        pass

    def set_states(self, states: list[QuestionState]) -> None:
        self._states = states
        self.refresh()

    def add(self, state: QuestionState) -> None:
        self._states.append(state)
        self.refresh()

    def remove(self, qid: str) -> None:
        self._states = [s for s in self._states if s.id != qid]
        self.refresh()

    @property
    def items(self) -> list[QuestionState]:
        return self._states
