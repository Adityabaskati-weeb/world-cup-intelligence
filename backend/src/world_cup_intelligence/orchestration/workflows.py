from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Callable

from world_cup_intelligence.config import metadata_path
from world_cup_intelligence.core.logging import get_logger
from world_cup_intelligence.orchestration.memory import ProjectMemoryStore


logger = get_logger(__name__)


@dataclass
class WorkflowStepResult:
    step: str
    status: str
    started_at: str
    finished_at: str


class WorkflowStateStore:
    def __init__(self) -> None:
        self.path = metadata_path("workflow_state.json")

    def load(self) -> dict[str, object]:
        if not self.path.exists():
            return {"runs": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def append_run(self, payload: dict[str, object]) -> None:
        state = self.load()
        runs = list(state.get("runs", []))
        runs.append(payload)
        self.path.write_text(json.dumps({"runs": runs}, indent=2), encoding="utf-8")


class PipelineOrchestrator:
    def __init__(self) -> None:
        self.memory_store = ProjectMemoryStore()
        self.state_store = WorkflowStateStore()

    def ensure_project_memory(self) -> None:
        self.memory_store.ensure_defaults()

    def execute(self, workflow_name: str, steps: list[tuple[str, Callable[[], object]]]) -> None:
        self.ensure_project_memory()
        run_started = datetime.now(UTC).isoformat()
        step_results: list[WorkflowStepResult] = []
        status = "completed"

        for step_name, step_callable in steps:
            started_at = datetime.now(UTC).isoformat()
            logger.info("Workflow %s starting step %s", workflow_name, step_name)
            try:
                step_callable()
                step_status = "completed"
            except Exception:
                step_status = "failed"
                status = "failed"
                raise
            finally:
                finished_at = datetime.now(UTC).isoformat()
                step_results.append(
                    WorkflowStepResult(
                        step=step_name,
                        status=step_status,
                        started_at=started_at,
                        finished_at=finished_at,
                    )
                )
                logger.info("Workflow %s finished step %s with status=%s", workflow_name, step_name, step_status)

        self.state_store.append_run(
            {
                "workflow_name": workflow_name,
                "status": status,
                "started_at": run_started,
                "finished_at": datetime.now(UTC).isoformat(),
                "steps": [step.__dict__ for step in step_results],
            }
        )
