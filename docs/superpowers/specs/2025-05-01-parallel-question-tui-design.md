# Dynamic TUI for Parallel Question Answering — Design

**Date:** 2025-05-01
**Status:** Approved

---

## 1. Overview

A terminal-based user interface for posing multiple questions to the RAG system and observing agent pipelines execute in parallel. Provides live visibility into each question's processing steps, token usage (input/output/reasoning), and final results — suitable for development debugging, live demos, and comparative analysis.

---

## 2. Architecture

### 2.1 Framework

**Textual** — modern Python TUI framework with reactive widgets, asyncio support, and built-in layout/keyboard handling.

```
┌─────────────────────────────────────────────────────────────┐
│  DASHBOARD                                                   │
│  ┌──────────┐  ┌──────────────────────────────────────────┐│
│  │ Question │  │  ACTIVE QUESTION CARD                    ││
│  │  List    │  │  ┌────────────────────────────────────┐  ││
│  │          │  │  │ Pipeline Steps (collapsible)       │  ││
│  │ Q1 ●     │  │  │  ● Query Planning  ✓ 1.2k/0.4k/0k  │  ││
│  │ Q2 ○     │  │  │  ● HyDE Gen      ✓ 2.1k/0.8k/0k   │  ││
│  │ Q3 ○     │  │  │  ● Web Search    ✓ 0.3k/1.5k/0k   │  ││
│  │          │  │  │  ● Retrieval     ✓ 0.5k/0.2k/0k   │  ││
│  │          │  │  │  ● Reranking     ✓ 0.4k/0.1k/0k   │  ││
│  │          │  │  │  ● Evidence Filt ✓ 0.6k/0.3k/0k   │  ││
│  │          │  │  │  ● Answer Write  ● ...  0.8k/??k  │  ││
│  │          │  │  │  ● Critic Loop   ○ pending        │  ││
│  │          │  │  └────────────────────────────────────┘  ││
│  │          │  │  ┌────────────────────────────────────┐  ││
│  │          │  │  │ Live Logs (expandable)             │  ││
│  │          │  │  └────────────────────────────────────┘  ││
│  │          │  └──────────────────────────────────────────┘│
│  └──────────┘  ┌──────────────────────────────────────────┐│
│               │  RESULTS PANEL                            ││
│               │  ┌────────────────────────────────────┐  ││
│               │  │ Final Answer                        │  ││
│               │  │ Critic: Grounded ✓ | Relevant ✓     │  ││
│               │  │ Sources: 5 cited                    │  ││
│               │  └────────────────────────────────────┘  ││
│               └──────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│  [A]dd  [C]ancel  [↑↓]Navigate  [Enter]Expand  [Q]uit     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Components

| Component | Responsibility |
|---|---|
| `Dashboard` | Root layout, manages global state and event bus |
| `QuestionList` | Scrollable sidebar showing all questions with status indicators |
| `QuestionCard` | Expanded view of a single question with pipeline steps and logs |
| `PipelineStep` | Individual step (QueryPlanning, HyDE, etc.) with token counts |
| `TokenMeter` | Displays in/out/reasoning tokens per step |
| `LogViewer` | Expandable live log stream for selected question |
| `ResultsPanel` | Final answer, critic verdict, sources |
| `StatusIndicator` | ● running  ○ pending  ✓ done  ✗ failed |

### 2.3 Concurrency Model

- Each question runs as an `asyncio.Task` in the `QuestionOrchestrator`
- A `QuestionState` dataclass per question tracks: status, current step, tokens, logs, result
- State changes published via `Events` (Textual reactive) to update UI reactively
- `TokenTracker` middleware on LLM calls accumulates per-step token counts

---

## 3. Data Model

### 3.1 Question State

```python
@dataclass
class QuestionState:
    id: str
    question: str
    status: Literal["pending", "running", "done", "failed", "cancelled"]
    current_step: str | None
    steps: list[StepState]
    logs: list[str]
    tokens_in: int = 0
    tokens_out: int = 0
    tokens_reasoning: int = 0
    result: AnswerResult | None
    error: str | None

@dataclass
class StepState:
    name: str
    status: Literal["pending", "running", "done", "failed"]
    tokens_in: int = 0
    tokens_out: int = 0
    tokens_reasoning: int = 0
    started_at: float | None = None
    finished_at: float | None = None
```

---

## 4. Interactions

| Key | Action |
|---|---|
| `a` | Add new question (opens input modal) |
| `c` | Cancel selected question |
| `↑/↓` | Navigate question list |
| `Enter` | Expand/collapse selected question's details |
| `l` | Toggle log viewer for selected question |
| `r` | Reorder selected question (move up/down in queue) |
| `q` | Quit (with confirmation if questions running) |

---

## 5. Token Tracking

Each LLM call wrapped by `TokenTracker` middleware:
- Captures `input_tokens`, `output_tokens`, and `completion_tokens` (reasoning if model supports it)
- Attributes tokens to the current pipeline step
- Running totals displayed per step and aggregated per question

Reasoning token support:
- OpenRouter/Anthropic models with extended thinking: tracked separately
- Other models: `completion_tokens` shown as `output_tokens`

---

## 6. File Structure

```
src/
├── tui/
│   ├── __init__.py
│   ├── dashboard.py      # Root app
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── question_list.py
│   │   ├── question_card.py
│   │   ├── pipeline_step.py
│   │   ├── token_meter.py
│   │   ├── log_viewer.py
│   │   └── results_panel.py
│   ├── orchestrator.py   # asyncio task management
│   ├── events.py         # Textual events
│   └── state.py          # QuestionState dataclasses
```

---

## 7. Dependencies

Add to `pyproject.toml`:
- `textual>=0.80.0`

Existing dependencies unchanged.

---

## 8. Scope

**In scope:**
- Multi-question parallel execution with live pipeline step visibility
- Token tracking per step (in/out/reasoning)
- Log streaming per question
- Cancel, navigate, expand interactions
- Results comparison view

**Out of scope (for v1):**
- Persistent configuration profiles
- Export to file (JSON/CSV) — available via existing `--save` CLI
- Distributed execution across machines