from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class StepState:
    name: str
    status: Literal["pending", "running", "done", "failed"] = "pending"
    tokens_in: int = 0
    tokens_out: int = 0
    tokens_reasoning: int = 0
    started_at: float | None = None
    finished_at: float | None = None

@dataclass
class QuestionState:
    id: str
    question: str
    status: Literal["pending", "running", "done", "failed", "cancelled"] = "pending"
    current_step: str | None = None
    steps: list[StepState] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0
    tokens_reasoning: int = 0
    result: AnswerResult | None = None
    error: str | None = None

@dataclass
class AnswerResult:
    answer: str
    is_grounded: bool
    is_relevant: bool
    comment: str
    sources_count: int