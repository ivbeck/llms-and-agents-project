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
