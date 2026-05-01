from __future__ import annotations

class TokenTracker:
    def __init__(self) -> None:
        self.tokens_in: int = 0
        self.tokens_out: int = 0
        self.tokens_reasoning: int = 0

    def reset(self) -> None:
        self.tokens_in = 0
        self.tokens_out = 0
        self.tokens_reasoning = 0

    def track(self, tokens_in: int, tokens_out: int, tokens_reasoning: int = 0) -> None:
        self.tokens_in += tokens_in
        self.tokens_out += tokens_out
        self.tokens_reasoning += tokens_reasoning