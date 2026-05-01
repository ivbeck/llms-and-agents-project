from src.tui.widgets.log_viewer import LogViewer

def test_log_viewer_initial():
    lv = LogViewer()
    assert len(lv.lines) == 0

def test_log_viewer_append():
    lv = LogViewer()
    lv.append("Starting search")
    assert "Starting search" in lv.lines