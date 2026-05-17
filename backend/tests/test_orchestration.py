from world_cup_intelligence.orchestration.memory import ProjectMemoryStore
from world_cup_intelligence.orchestration.workflows import PipelineOrchestrator


def test_project_memory_defaults_are_persisted() -> None:
    store = ProjectMemoryStore()
    memory = store.ensure_defaults()
    assert memory.project_goals
    assert store.memory_file.exists()
    assert store.markdown_file.exists()


def test_pipeline_orchestrator_records_workflow_runs() -> None:
    orchestrator = PipelineOrchestrator()

    def noop() -> None:
        return None

    orchestrator.execute("unit_test_workflow", [("noop_step", noop)])
    state = orchestrator.state_store.load()
    assert any(run["workflow_name"] == "unit_test_workflow" for run in state["runs"])
