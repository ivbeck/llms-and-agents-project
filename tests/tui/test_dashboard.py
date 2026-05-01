from unittest.mock import MagicMock

from src.tui.dashboard import Dashboard


def test_dashboard_initializes():
    mock_settings = MagicMock()
    mock_settings.openrouter_api_key = "test-key"
    mock_settings.tavily_api_key = "test-key"
    app = Dashboard(settings=mock_settings)
    assert app.orchestrator is not None
