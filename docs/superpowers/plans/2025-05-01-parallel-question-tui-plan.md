# Parallel Question TUI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Textual-based TUI dashboard that runs multiple RAG questions in parallel with live pipeline step visibility and per-step token tracking.

**Architecture:** The TUI runs as a standalone app (`rag-tui` CLI entry point) that imports the existing `AdvancedMultiAgentRAGSystem`. Each question is wrapped as an `asyncio.Task` managed by a `QuestionOrchestrator`. State flows through Textual reactive events. Token tracking is injected via a middleware wrapper around `OpenRouterLLM.complete()`.

**Tech Stack:** textual>=0.80.0, asyncio, existing project models/orchestrator/agents

---

## File Structure

```
src/
├── tui/
│   ├── __init__.py
│   ├── dashboard.py      # Root Textual App, global state, event bus
│   ├── cli.py            # CLI entry point: rag-tui
│   ├── orchestrator.py   # asyncio task management for question runs
│   ├── events.py         # QuestionStatechanged, TokenAccumulated, LogAppended
│   ├── state.py          # QuestionState, StepState, AnswerResult dataclasses
│   └── widgets/
│       ├── __init__.py
│       ├── question_list.py   # Scrollable sidebar list
│       ├── question_card.py   # Expanded card for selected question
│       ├── pipeline_step.py   # Individual step with status + token counts
│       ├── token_meter.py     # in/out/reasoning token display
│       ├── log_viewer.py      # Expandable live log stream
│       └── results_panel.py   # Final answer + critic verdict + sources
tests/
└── tui/
    ├── __init__.py
    ├── test_state.py
    ├── test_orchestrator.py
    ├── test_events.py
    └── test_widgets/
        ├── __init__.py
        ├── test_question_list.py
        ├── test_question_card.py
        ├── test_pipeline_step.py
        ├── test_token_meter.py
        ├── test_log_viewer.py
        └── test_results_panel.py
```

---

## Task 1: State dataclasses

**Files:**
- Create: `src/tui/state.py`
- Test: `tests/tui/test_state.py`

- [ ] **Step 1: Write failing test**

```python
# tests/tui/test_state.py
from src.tui.state import QuestionState, StepState

def test_question_state_defaults():
    qs = QuestionState(id="q1", question="What is x?")
    assert qs.status == "pending"
    assert qs.steps == []
    assert qs.logs == []
    assert qs.tokens_in == 0
    assert qs.tokens_out == 0
    assert qs.tokens_reasoning == 0
    assert qs.result is None
    assert qs.error is None

def test_step_state_defaults():
    ss = StepState(name="QueryPlanning")
    assert ss.status == "pending"
    assert ss.tokens_in == 0
    assert ss.tokens_out == 0
    assert ss.tokens_reasoning == 0
    assert ss.started_at is None
    assert ss.finished_at is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tui/test_state.py -v`
Expected: FAIL — src/tui/state.py does not exist

- [ ] **Step 3: Write minimal implementation**

```python
# src/tui/state.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/tui/test_state.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/tui/test_state.py src/tui/state.py
git commit -m "feat(tui): add QuestionState and StepState dataclasses"
```

---

## Task 2: Textual Events

**Files:**
- Create: `src/tui/events.py`
- Test: `tests/tui/test_events.py`

- [ ] **Step 1: Write failing test**

```python
# tests/tui/test_events.py
from src.tui.events import QuestionStateChanged, TokenAccumulated, LogAppended

def test_question_state_changed():
    evt = QuestionStateChanged(question_id="q1", status="running", current_step="HyDE Gen")
    assert evt.question_id == "q1"
    assert evt.status == "running"
    assert evt.current_step == "HyDE Gen"

def test_token_accumulated():
    evt = TokenAccumulated(question_id="q1", step_name="QueryPlanning", tokens_in=100, tokens_out=40, tokens_reasoning=0)
    assert evt.question_id == "q1"
    assert evt.tokens_in == 100
    assert evt.tokens_out == 40

def test_log_appended():
    evt = LogAppended(question_id="q1", message="Search completed")
    assert evt.message == "Search completed"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tui/test_events.py -v`
Expected: FAIL — src/tui/events.py does not exist

- [ ] **Step 3: Write minimal implementation**

```python
# src/tui/events.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/tui/test_events.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/tui/test_events.py src/tui/events.py
git commit -m "feat(tui): add Textual event classes"
```

---

## Task 3: Token Tracker middleware

**Files:**
- Modify: `src/llm/openrouter_client.py:33-41`
- Create: `tests/tui/test_token_tracker.py`

The token tracker wraps `OpenRouterLLM.complete()` and fires `TokenAccumulated` events so the TUI can track per-step usage.

- [ ] **Step 1: Write failing test**

```python
# tests/tui/test_token_tracker.py
from src.tui.token_tracker import TokenTracker

def test_token_tracker_initialization():
    tracker = TokenTracker()
    assert tracker.tokens_in == 0
    assert tracker.tokens_out == 0
    assert tracker.tokens_reasoning == 0

def test_token_tracker_reset():
    tracker = TokenTracker()
    tracker.tokens_in = 100
    tracker.tokens_out = 50
    tracker.tokens_reasoning = 20
    tracker.reset()
    assert tracker.tokens_in == 0
    assert tracker.tokens_out == 0
    assert tracker.tokens_reasoning == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tui/test_token_tracker.py -v`
Expected: FAIL — src/tui/token_tracker.py does not exist

- [ ] **Step 3: Write minimal implementation**

```python
# src/tui/token_tracker.py
from __future__ import annotations
from typing import Callable

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/tui/test_token_tracker.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/tui/test_token_tracker.py src/tui/token_tracker.py
git commit -m "feat(tui): add TokenTracker middleware"
```

---

## Task 4: QuestionOrchestrator

**Files:**
- Create: `src/tui/orchestrator.py`
- Test: `tests/tui/test_orchestrator.py`

The orchestrator owns the asyncio task lifecycle. It maps pipeline steps to `StepState` objects, emits events, and drives `AdvancedMultiAgentRAGSystem.answer_question()` as an async task.

Step names (in order): `QueryPlanning`, `HyDE Gen`, `Web Search`, `Retrieval`, `Reranking`, `Evidence Filter`, `Answer Write`, `Critic Loop`

- [ ] **Step 1: Write failing test**

```python
# tests/tui/test_orchestrator.py
import asyncio
from src.tui.orchestrator import QuestionOrchestrator
from src.tui.state import QuestionState

def test_orchestrator_initialization():
    orch = QuestionOrchestrator()
    assert len(orch._tasks) == 0

def test_orchestrator_add_question():
    orch = QuestionOrchestrator()
    qid = orch.add_question("What is AI?")
    assert qid in orch._states
    state = orch._states[qid]
    assert state.question == "What is AI?"
    assert state.status == "pending"

def test_orchestrator_cancel():
    orch = QuestionOrchestrator()
    qid = orch.add_question("Test?")
    orch.cancel_question(qid)
    assert orch._states[qid].status == "cancelled"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tui/test_orchestrator.py -v`
Expected: FAIL — src/tui/orchestrator.py does not exist

- [ ] **Step 3: Write minimal implementation**

```python
# src/tui/orchestrator.py
from __future__ import annotations
import asyncio
import logging
import uuid
from typing import Callable

from src.config import Settings
from src.orchestrator import AdvancedMultiAgentRAGSystem
from src.tui.events import QuestionStateChanged, TokenAccumulated, LogAppended
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
    def __init__(self, settings: Settings, event_bus: Callable[[str, tuple], None] | None = None) -> None:
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
        state = self._states[qid]
        state.status = "running"
        self._emit("QuestionStateChanged", (qid, "running", None))
        task = asyncio.create_task(self._run_pipeline(qid))
        self._tasks[qid] = task

    async def _run_pipeline(self, qid: str) -> None:
        state = self._states[qid]
        try:
            rag = AdvancedMultiAgentRAGSystem(self.settings)
            self._set_step(qid, "QueryPlanning", "running")
            result = rag.answer_question(state.question)
            answer_result = AnswerResult(
                answer=result.answer,
                is_grounded=result.critic.is_grounded,
                is_relevant=result.critic.is_relevant,
                comment=result.critic.comment,
                sources_count=len(result.sources),
            )
            state.result = answer_result
            self._set_step(qid, "Critic Loop", "done")
            state.status = "done"
            self._emit("QuestionStateChanged", (qid, "done", "Critic Loop"))
        except Exception as exc:
            state.status = "failed"
            state.error = str(exc)
            self._emit("QuestionStateChanged", (qid, "failed", None))
            logger.exception("Question %s failed", qid)

    def _set_step(self, qid: str, step_name: str, status: str) -> None:
        state = self._states[qid]
        state.current_step = step_name
        for step in state.steps:
            if step.name == step_name:
                step.status = status  # type: ignore
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
        return list(self._states.values())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/tui/test_orchestrator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/tui/test_orchestrator.py src/tui/orchestrator.py
git commit -m "feat(tui): add QuestionOrchestrator with asyncio task management"
```

---

## Task 5: PipelineStep widget

**Files:**
- Create: `src/tui/widgets/pipeline_step.py`
- Test: `tests/tui/test_widgets/test_pipeline_step.py`

- [ ] **Step 1: Write failing test**

```python
# tests/tui/test_widgets/test_pipeline_step.py
from textual.app import App
from src.tui.widgets.pipeline_step import PipelineStep

def test_pipeline_step_initial_status():
    step = PipelineStep(name="QueryPlanning", status="pending")
    assert step.name == "QueryPlanning"
    assert step.has_status("pending")

def test_pipeline_step_update():
    step = PipelineStep(name="HyDE Gen", status="pending")
    step.update_status("done", tokens_in=200, tokens_out=80, tokens_reasoning=0)
    assert step.has_status("done")
    assert step.tokens_in == 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tui/test_widgets/test_pipeline_step.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/tui/widgets/pipeline_step.py
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

    def has_status(self, status: str) -> bool:
        return self._status == status

    def update_status(self, status: str, tokens_in: int = 0, tokens_out: int = 0, tokens_reasoning: int = 0) -> None:
        self._status = status
        self.tokens_in = tokens_in
        self.tokens_out = tokens_out
        self.tokens_reasoning = tokens_reasoning
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/tui/test_widgets/test_pipeline_step.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/tui/test_widgets/test_pipeline_step.py src/tui/widgets/pipeline_step.py
git commit -m "feat(tui): add PipelineStep widget"
```

---

## Task 6: TokenMeter widget

**Files:**
- Create: `src/tui/widgets/token_meter.py`
- Test: `tests/tui/test_widgets/test_token_meter.py`

- [ ] **Step 1: Write failing test**

```python
# tests/tui/test_widgets/test_token_meter.py
from src.tui.widgets.token_meter import TokenMeter

def test_token_meter_defaults():
    tm = TokenMeter()
    assert tm.tokens_in == 0
    assert tm.tokens_out == 0

def test_token_meter_update():
    tm = TokenMeter()
    tm.update(1200, 400, 0)
    assert tm.tokens_in == 1200
    assert tm.tokens_out == 400
    assert tm.tokens_reasoning == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tui/test_widgets/test_token_meter.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/tui/widgets/token_meter.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/tui/test_widgets/test_token_meter.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/tui/test_widgets/test_token_meter.py src/tui/widgets/token_meter.py
git commit -m "feat(tui): add TokenMeter widget"
```

---

## Task 7: QuestionList widget

**Files:**
- Create: `src/tui/widgets/question_list.py`
- Test: `tests/tui/test_widgets/test_question_list.py`

- [ ] **Step 1: Write failing test**

```python
# tests/tui/test_widgets/test_question_list.py
from src.tui.widgets.question_list import QuestionList
from src.tui.state import QuestionState

def test_question_list_initial():
    ql = QuestionList()
    assert len(ql.items) == 0

def test_question_list_add():
    ql = QuestionList()
    state = QuestionState(id="q1", question="What is x?")
    ql.add(state)
    assert len(ql.items) == 1
    assert ql.items[0].id == "q1"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tui/test_widgets/test_question_list.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/tui/widgets/question_list.py
from __future__ import annotations
from textual.widget import Widget
from src.tui.state import QuestionState

class QuestionList(Widget):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.items: list[QuestionState] = []

    def add(self, state: QuestionState) -> None:
        self.items.append(state)

    def remove(self, qid: str) -> None:
        self.items = [s for s in self.items if s.id != qid]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/tui/test_widgets/test_question_list.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/tui/test_widgets/test_question_list.py src/tui/widgets/question_list.py
git commit -m "feat(tui): add QuestionList widget"
```

---

## Task 8: QuestionCard widget

**Files:**
- Create: `src/tui/widgets/question_card.py`
- Test: `tests/tui/test_widgets/test_question_card.py`

- [ ] **Step 1: Write failing test**

```python
# tests/tui/test_widgets/test_question_card.py
from src.tui.widgets.question_card import QuestionCard
from src.tui.state import QuestionState, StepState

def test_question_card_binds_state():
    qs = QuestionState(id="q1", question="What is AI?", steps=[StepState(name="QueryPlanning")])
    card = QuestionCard(qs)
    assert card.question == "What is AI?"
    assert len(card.steps) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tui/test_widgets/test_question_card.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/tui/widgets/question_card.py
from __future__ import annotations
from textual.widget import Widget
from src.tui.state import QuestionState, StepState

class QuestionCard(Widget):
    def __init__(self, state: QuestionState, **kwargs) -> None:
        super().__init__(**kwargs)
        self._state = state

    @property
    def question(self) -> str:
        return self._state.question

    @property
    def steps(self) -> list[StepState]:
        return self._state.steps
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/tui/test_widgets/test_question_card.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/tui/test_widgets/test_question_card.py src/tui/widgets/question_card.py
git commit -m "feat(tui): add QuestionCard widget"
```

---

## Task 9: LogViewer widget

**Files:**
- Create: `src/tui/widgets/log_viewer.py`
- Test: `tests/tui/test_widgets/test_log_viewer.py`

- [ ] **Step 1: Write failing test**

```python
# tests/tui/test_widgets/test_log_viewer.py
from src.tui.widgets.log_viewer import LogViewer

def test_log_viewer_initial():
    lv = LogViewer()
    assert len(lv.lines) == 0

def test_log_viewer_append():
    lv = LogViewer()
    lv.append("Starting search")
    assert "Starting search" in lv.lines
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tui/test_widgets/test_log_viewer.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/tui/widgets/log_viewer.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/tui/test_widgets/test_log_viewer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/tui/test_widgets/test_log_viewer.py src/tui/widgets/log_viewer.py
git commit -m "feat(tui): add LogViewer widget"
```

---

## Task 10: ResultsPanel widget

**Files:**
- Create: `src/tui/widgets/results_panel.py`
- Test: `tests/tui/test_widgets/test_results_panel.py`

- [ ] **Step 1: Write failing test**

```python
# tests/tui/test_widgets/test_results_panel.py
from src.tui.widgets.results_panel import ResultsPanel
from src.tui.state import AnswerResult

def test_results_panel_empty():
    rp = ResultsPanel()
    assert rp.answer == ""

def test_results_panel_bind():
    result = AnswerResult(answer="AI is artificial intelligence.", is_grounded=True, is_relevant=True, comment="ok", sources_count=3)
    rp = ResultsPanel()
    rp.bind_result(result)
    assert rp.answer == "AI is artificial intelligence."
    assert rp.sources_count == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tui/test_widgets/test_results_panel.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/tui/widgets/results_panel.py
from __future__ import annotations
from textual.widget import Widget
from src.tui.state import AnswerResult

class ResultsPanel(Widget):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._result: AnswerResult | None = None

    @property
    def answer(self) -> str:
        if self._result is None:
            return ""
        return self._result.answer

    @property
    def sources_count(self) -> int:
        if self._result is None:
            return 0
        return self._result.sources_count

    def bind_result(self, result: AnswerResult) -> None:
        self._result = result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/tui/test_widgets/test_results_panel.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/tui/test_widgets/test_results_panel.py src/tui/widgets/results_panel.py
git commit -m "feat(tui): add ResultsPanel widget"
```

---

## Task 11: Dashboard (Root App)

**Files:**
- Create: `src/tui/dashboard.py`
- Test: `tests/tui/test_dashboard.py`

This is the root Textual `App` subclass. It owns the `QuestionOrchestrator`, arranges all widgets in the layout shown in the spec, and wires keyboard bindings.

- [ ] **Step 1: Write failing test**

```python
# tests/tui/test_dashboard.py
from src.tui.dashboard import Dashboard

def test_dashboard_initializes():
    app = Dashboard()
    assert app.orchestrator is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tui/test_dashboard.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/tui/dashboard.py
from __future__ import annotations
from textual.app import App
from src.config import Settings
from src.tui.orchestrator import QuestionOrchestrator

class Dashboard(App):
    def __init__(self, settings: Settings | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._settings = settings or Settings()
        self.orchestrator = QuestionOrchestrator(self._settings)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/tui/test_dashboard.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/tui/test_dashboard.py src/tui/dashboard.py
git commit -m "feat(tui): add Dashboard root App"
```

---

## Task 12: CLI entry point

**Files:**
- Create: `src/tui/cli.py`
- Modify: `pyproject.toml:36`

- [ ] **Step 1: Write failing test**

```python
# tests/tui/test_cli.py
from src.tui.cli import build_parser

def test_parser_builds():
    parser = build_parser()
    assert parser is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tui/test_cli.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/tui/cli.py
from __future__ import annotations
import argparse
from textual.driver import Driver

from src.config import Settings
from src.tui.dashboard import Dashboard

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rag-tui", description="Parallel Question TUI")
    return parser

async def run_tui(settings: Settings, driver_class: type[Driver] | None = None) -> None:
    app = Dashboard(settings)
    await app.run_async()

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = Settings()
    import asyncio
    asyncio.run(run_tui(settings))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/tui/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/tui/test_cli.py src/tui/cli.py
git commit -m "feat(tui): add rag-tui CLI entry point"
```

- [ ] **Step 6: Update pyproject.toml**

Add `rag-tui = "src.tui.cli:main"` to `[project.scripts]`

---

## Task 13: Wire text processing into orchestrator

After all widgets are in place, update `QuestionOrchestrator._run_pipeline()` to actually emit step lifecycle events (`QuestionStateChanged`) for each pipeline step as `AdvancedMultiAgentRAGSystem.answer_question()` executes.

- [ ] **Step 1: Update orchestrator to call _set_step for each step**

Modify `src/tui/orchestrator.py` — `_run_pipeline()` calls `self._set_step(qid, step_name, "running")` before each logical phase and `self._set_step(qid, step_name, "done")` after. Steps map to pipeline phases as defined in `STEP_NAMES`.

- [ ] **Step 2: Run integration verification**

Run: `pytest tests/tui/ -v`
Expected: PASS (all tests)

- [ ] **Step 3: Commit**

```bash
git add src/tui/orchestrator.py
git commit -m "feat(tui): wire step lifecycle events into orchestrator"
```

---

## Task 14: Final integration and smoke test

- [ ] **Step 1: Add `textual` to pyproject.toml dependencies**

- [ ] **Step 2: Run full test suite**

Run: `pytest tests/tui/ -v && ruff check src/tui/ && mypy src/tui/`
Expected: All pass

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "deps: add textual>=0.80.0"
```
