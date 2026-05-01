from __future__ import annotations
from textual.widget import Widget
from textual.widgets import Static

class PipelineStep(Widget):
    def __init__(self, name: str, status: str = "pending", **kwargs) -> None:
        super().__init__(**kwargs)
        self._name = name
        self._status = status
        self.tokens_in = 0
        self.tokens_out = 0
        self.tokens_reasoning = 0

    @property
    def name(self) -> str:
        return self._name

    def has_status(self, status: str) -> bool:
        return self._status == status

    def update_status(self, status: str, tokens_in: int = 0, tokens_out: int = 0, tokens_reasoning: int = 0) -> None:
        self._status = status
        self.tokens_in = tokens_in
        self.tokens_out = tokens_out
        self.tokens_reasoning = tokens_reasoning