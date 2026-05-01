from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static

from src.config import Settings
from src.tui.orchestrator import QuestionOrchestrator
from src.tui.widgets.question_list import QuestionList
from src.tui.widgets.question_card import QuestionCard
from src.tui.widgets.results_panel import ResultsPanel


class Dashboard(App):
    CSS = """
    Screen {
        background: #1a1a2e;
    }
    #sidebar {
        width: 30;
        background: #16213e;
        border-right: solid #0f3460;
    }
    #main {
        background: #1a1a2e;
    }
    #question-display {
        background: #16213e;
        padding: 1;
    }
    #results-display {
        background: #16213e;
        border-top: solid #0f3460;
        padding: 1;
    }
    .header-title {
        padding: 1 2;
        background: #0f3460;
        color: #e8e8e8;
        text-style: bold;
    }
    .question-item {
        padding: 1 2;
        color: #a8a8a8;
    }
    .question-item.selected {
        background: #0f3460;
        color: #e8e8e8;
    }
    .step {
        padding: 0 2;
        color: #a8a8a8;
    }
    .step-running {
        color: #f0a500;
    }
    .step-done {
        color: #4ecca3;
    }
    .step-failed {
        color: #ff6b6b;
    }
    #question-text {
        padding: 1 2;
        background: #0f3460;
        color: #e8e8e8;
        text-style: bold;
    }
    #steps-label {
        padding: 1 2;
        color: #a8a8a8;
    }
    #answer-text {
        padding: 1 2;
        color: #e8e8e8;
    }
    #critic-verdict {
        padding: 0 2;
        color: #4ecca3;
    }
    #sources-count {
        padding: 0 2;
        color: #a8a8a8;
    }
    #critic-comment {
        padding: 0 2;
        color: #a8a8a8;
    }
    #empty-message {
        padding: 1 2;
        color: #666;
    }
    """

    BINDINGS = [
        ("a", "add_question", "Add"),
        ("c", "cancel_question", "Cancel"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, settings: Settings | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._settings = settings
        self.orchestrator = QuestionOrchestrator(self._settings)
        self._selected_qid: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("Questions", classes="header-title")
                yield QuestionList(id="question-list")
            with Vertical(id="main"):
                with Vertical(id="question-display"):
                    yield QuestionCard(id="question-card")
                with Vertical(id="results-display"):
                    yield Static("Results", classes="header-title")
                    yield ResultsPanel(id="results-panel")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Parallel Question TUI"

    def action_add_question(self) -> None:
        qid = self.orchestrator.add_question("New question")
        self._selected_qid = qid
        self.query_one("#question-list", QuestionList).selected_id = qid
        self.query_one("#question-card", QuestionCard).selected_id = qid

    def action_cancel_question(self) -> None:
        if self._selected_qid:
            self.orchestrator.cancel_question(self._selected_qid)

    def action_quit(self) -> None:
        self.exit()
