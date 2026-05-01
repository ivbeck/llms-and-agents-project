from __future__ import annotations

from textual.app import App

from src.config import Settings
from src.tui.orchestrator import QuestionOrchestrator


class Dashboard(App):
    def __init__(self, settings: Settings | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._settings = settings or Settings()
        self.orchestrator = QuestionOrchestrator(self._settings)
