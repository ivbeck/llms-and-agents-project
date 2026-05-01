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