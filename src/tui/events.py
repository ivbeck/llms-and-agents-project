from __future__ import annotations
from textual.events import Event

class QuestionStateChanged(Event):
    def __init__(self, question_id: str, status: str, current_step: str | None = None) -> None:
        super().__init__()
        self.question_id = question_id
        self.status = status
        self.current_step = current_step

class TokenAccumulated(Event):
    def __init__(self, question_id: str, step_name: str, tokens_in: int, tokens_out: int, tokens_reasoning: int) -> None:
        super().__init__()
        self.question_id = question_id
        self.step_name = step_name
        self.tokens_in = tokens_in
        self.tokens_out = tokens_out
        self.tokens_reasoning = tokens_reasoning

class LogAppended(Event):
    def __init__(self, question_id: str, message: str) -> None:
        super().__init__()
        self.question_id = question_id
        self.message = message