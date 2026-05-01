from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Callable
from typing import Literal

from src.config import Settings
from src.orchestrator import AdvancedMultiAgentRAGSystem
from src.tui.state import AnswerResult, QuestionState, StepState

logger = logging.getLogger(__name__)

STEP_NAMES = [
    "QueryPlanning",
    "HyDE Gen",
    "Web Search",
    "Retrieval",
    "Reranking",
    "Evidence Filter",
    "Answer Write",
    "Critic Loop",
]

class QuestionOrchestrator:
    def __init__(self, settings: Settings | None = None, event_bus: Callable[[str, tuple], None] | None = None) -> None:
        self.settings = settings
        self.event_bus = event_bus or (lambda *_: None)
        self._states: dict[str, QuestionState] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}

    def _emit(self, event_name: str, args: tuple) -> None:
        self.event_bus(event_name, args)

    def add_question(self, question: str) -> str:
        qid = str(uuid.uuid4())[:8]
        steps = [StepState(name=name) for name in STEP_NAMES]
        state = QuestionState(id=qid, question=question, steps=steps)
        self._states[qid] = state
        return qid

    def start_question(self, qid: str) -> None:
        if qid not in self._states:
            raise KeyError(f"No question found with id: {qid}")
        state = self._states[qid]
        state.status = "running"
        self._emit("QuestionStateChanged", (qid, "running", None))
        task = asyncio.create_task(self._run_pipeline(qid))
        self._tasks[qid] = task

    async def _run_pipeline(self, qid: str) -> None:
        state = self._states[qid]
        try:
            rag = AdvancedMultiAgentRAGSystem(self.settings)
            for step_name in STEP_NAMES[:4]:
                self._set_step(qid, step_name, "running")
            result = rag.answer_question(state.question)
            answer_result = AnswerResult(
                answer=result.answer,
                is_grounded=result.critic.is_grounded,
                is_relevant=result.critic.is_relevant,
                comment=result.critic.comment,
                sources_count=len(result.sources),
            )
            state.result = answer_result
            for step_name in STEP_NAMES[4:-1]:
                self._set_step(qid, step_name, "done")
            state.status = "done"
            self._emit("QuestionStateChanged", (qid, "done", "Critic Loop"))
        except asyncio.CancelledError:
            state.status = "cancelled"
            self._emit("QuestionStateChanged", (qid, "cancelled", None))
            raise
        except Exception as exc:
            state.status = "failed"
            state.error = str(exc)
            self._emit("QuestionStateChanged", (qid, "failed", None))
            logger.exception("Question %s failed", qid)

    def _set_step(self, qid: str, step_name: str, status: Literal["pending", "running", "done", "failed"]) -> None:
        if qid not in self._states:
            raise KeyError(f"No question found with id: {qid}")
        state = self._states[qid]
        state.current_step = step_name
        for step in state.steps:
            if step.name == step_name:
                step.status = status
                break
        self._emit("QuestionStateChanged", (qid, state.status, step_name))

    def cancel_question(self, qid: str) -> None:
        if qid in self._tasks:
            self._tasks[qid].cancel()
        if qid in self._states:
            self._states[qid].status = "cancelled"
            self._emit("QuestionStateChanged", (qid, "cancelled", None))

    def get_state(self, qid: str) -> QuestionState | None:
        return self._states.get(qid)

    def get_all_states(self) -> list[QuestionState]:
        return [state for state in self._states.values()]
