from __future__ import annotations

import pandas as pd

from world_cup_intelligence.orchestration.workflows import PipelineOrchestrator
from world_cup_intelligence.services.training import train_xg_model


def synthetic_xg_frame() -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []
    for cycle in range(12):
        rows.extend(
            [
                {
                    "distance": 8.0 + cycle * 0.35,
                    "angle": 0.74 - cycle * 0.015,
                    "minute": 10 + cycle * 3,
                    "pressure": 0.10 + cycle * 0.01,
                    "game_state": 0 if cycle % 3 else 1,
                    "body_part_code": 1,
                    "shot_type_code": 0,
                    "is_goal": 1,
                },
                {
                    "distance": 18.5 + cycle * 0.4,
                    "angle": 0.26 - cycle * 0.004,
                    "minute": 22 + cycle * 4,
                    "pressure": 0.34 + cycle * 0.015,
                    "game_state": -1 if cycle % 2 else 1,
                    "body_part_code": 0 if cycle % 2 else 2,
                    "shot_type_code": 1 if cycle % 3 else 2,
                    "is_goal": 0,
                },
            ]
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    orchestrator = PipelineOrchestrator()

    def _run() -> None:
        artifact = train_xg_model(synthetic_xg_frame())
        print(artifact)

    orchestrator.execute(workflow_name="train_xg_model", steps=[("train_xg_model", _run)])
