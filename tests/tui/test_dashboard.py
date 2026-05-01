from src.tui.dashboard import Dashboard


def test_dashboard_initializes():
    app = Dashboard()
    assert app.orchestrator is not None