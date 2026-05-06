from __future__ import annotations

from textual.widget import Widget
from textual.widgets import Static
from textual.reactive import reactive

from src.tui.state import QuestionState, StepState


class QuestionCard(Widget):
    selected_id: reactive[str | None] = reactive(None)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._state: QuestionState | None = None

    @property
    def question(self) -> str:
        return self._state.question if self._state else ""

    @property
    def steps(self) -> list[StepState]:
        return self._state.steps if self._state else []

    def watch_selected_id(self, qid: str | None) -> None:
        if qid:
            self._state = self._get_state(qid)
            self.refresh()
        else:
            self._state = None
            self.refresh()

    def _get_state(self, qid: str) -> QuestionState | None:
        from src.tui.dashboard import Dashboard
        app = self.app
        if isinstance(app, Dashboard):
            return app.orchestrator.get_state(qid)
        return None

    def compose(self):
        if self._state is None:
            yield Static("No question selected")
            return

        yield Static(self._state.question, id="question-text")
        yield Static("Pipeline Steps:", id="steps-label")
        for step in self._state.steps:
            status_icon = self._status_icon(step.status)
            yield Static(f"{status_icon} {step.name}  in={step.tokens_in} out={step.tokens_out}",
                        classes=f"step step-{step.status}")

    def _status_icon(self, status: str) -> str:
        return {"pending": "○", "running": "●", "done": "✓", "failed": "✗"}.get(status, "○")

    def bind_state(self, state: QuestionState) -> None:
        self._state = state
        self.refresh()
