import asyncio
from unittest.mock import MagicMock, patch
import pytest

from src.tui.orchestrator import QuestionOrchestrator
from src.tui.state import QuestionState, StepState


def test_orchestrator_initialization():
    orch = QuestionOrchestrator()
    assert len(orch._tasks) == 0
    assert len(orch._states) == 0


def test_orchestrator_add_question():
    orch = QuestionOrchestrator()
    qid = orch.add_question("What is AI?")
    assert qid in orch._states
    state = orch._states[qid]
    assert state.question == "What is AI?"
    assert state.status == "pending"
    assert len(state.steps) == 9
    step_names = [s.name for s in state.steps]
    assert step_names == [
        "QueryPlanning",
        "HyDE Gen",
        "Web Search",
        "Retrieval",
        "Reranking",
        "Evidence Filter",
        "Evidence Sufficiency",
        "Answer Write",
        "Critic Loop",
    ]


def test_orchestrator_cancel():
    orch = QuestionOrchestrator()
    qid = orch.add_question("Test?")
    orch.cancel_question(qid)
    assert orch._states[qid].status == "cancelled"


def test_orchestrator_start_question():
    mock_settings = MagicMock()
    mock_settings.enable_hyde = False
    mock_settings.enable_iterative_retrieval = False
    mock_settings.enable_self_rag = False
    mock_settings.enable_evidence_filtering = False
    mock_settings.enable_evidence_sufficiency = False
    mock_settings.enable_query_decomposition = False
    mock_settings.enable_cross_encoder_reranking = False
    mock_settings.enable_hybrid_retrieval = False
    mock_settings.max_iterations = 1
    mock_settings.reflection_steps = 1
    mock_settings.top_k_chunks = 8
    mock_settings.filter_top_k = 6

    mock_result = MagicMock()
    mock_result.answer = "Test answer"
    mock_result.critic.is_grounded = True
    mock_result.critic.is_relevant = True
    mock_result.critic.comment = "Good"
    mock_result.sources = []

    async def run_test():
        with patch("src.tui.orchestrator.AdvancedMultiAgentRAGSystem") as MockRAG:
            MockRAG.return_value.answer_question.return_value = mock_result
            orch = QuestionOrchestrator(settings=mock_settings)
            qid = orch.add_question("What is AI?")
            orch.start_question(qid)

            state = orch.get_state(qid)
            assert state.status == "running"
            assert len(orch._tasks) == 1

    asyncio.run(run_test())


def test_get_state():
    orch = QuestionOrchestrator()
    qid = orch.add_question("Test?")
    state = orch.get_state(qid)
    assert state is not None
    assert state.question == "Test?"

    nonexistent = orch.get_state("nonexistent")
    assert nonexistent is None


def test_get_all_states():
    orch = QuestionOrchestrator()
    qid1 = orch.add_question("Question 1")
    qid2 = orch.add_question("Question 2")
    states = orch.get_all_states()
    assert len(states) == 2
    assert any(s.question == "Question 1" for s in states)
    assert any(s.question == "Question 2" for s in states)
