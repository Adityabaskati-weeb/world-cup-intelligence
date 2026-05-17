from __future__ import annotations

import pandas as pd

from world_cup_intelligence.orchestration.workflows import PipelineOrchestrator
from world_cup_intelligence.services.training import train_penalty_models


def synthetic_penalty_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"pressure": 0.80, "footedness_code": 1, "keeper_bias": 0.35, "match_state": 1, "target_zone": 2, "scored": 1},
            {"pressure": 0.75, "footedness_code": 0, "keeper_bias": 0.45, "match_state": 0, "target_zone": 0, "scored": 0},
            {"pressure": 0.65, "footedness_code": 1, "keeper_bias": 0.20, "match_state": -1, "target_zone": 1, "scored": 1},
            {"pressure": 0.90, "footedness_code": 1, "keeper_bias": 0.55, "match_state": 1, "target_zone": 2, "scored": 0},
            {"pressure": 0.55, "footedness_code": 0, "keeper_bias": 0.18, "match_state": 0, "target_zone": 1, "scored": 1},
            {"pressure": 0.70, "footedness_code": 1, "keeper_bias": 0.30, "match_state": 0, "target_zone": 2, "scored": 1},
        ]
    )


if __name__ == "__main__":
    orchestrator = PipelineOrchestrator()

    def _run() -> None:
        artifact = train_penalty_models(synthetic_penalty_frame())
        print(artifact)

    orchestrator.execute(workflow_name="train_penalty_model", steps=[("train_penalty_model", _run)])
