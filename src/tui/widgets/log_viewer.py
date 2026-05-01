from __future__ import annotations
from textual.widget import Widget

class LogViewer(Widget):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._lines: list[str] = []

    @property
    def lines(self) -> list[str]:
        return self._lines

    def append(self, message: str) -> None:
        self._lines.append(message)