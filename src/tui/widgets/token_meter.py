from __future__ import annotations
from textual.widget import Widget

class TokenMeter(Widget):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.tokens_in: int = 0
        self.tokens_out: int = 0
        self.tokens_reasoning: int = 0

    def update(self, tokens_in: int, tokens_out: int, tokens_reasoning: int) -> None:
        self.tokens_in = tokens_in
        self.tokens_out = tokens_out
        self.tokens_reasoning = tokens_reasoning