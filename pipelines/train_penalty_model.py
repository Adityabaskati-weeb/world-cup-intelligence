from __future__ import annotations

import pandas as pd

from world_cup_intelligence.orchestration.workflows import PipelineOrchestrator
from world_cup_intelligence.services.training import train_penalty_models


def synthetic_penalty_frame() -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []
    for cycle in range(8):
        rows.extend(
            [
                {
                    "pressure": 0.78 + cycle * 0.01,
                    "footedness_code": 1,
                    "keeper_bias": 0.32 + cycle * 0.01,
                    "match_state": 1,
                    "target_zone": "low-right",
                    "scored": 1 if cycle % 4 else 0,
                },
                {
                    "pressure": 0.62 + cycle * 0.015,
                    "footedness_code": 0,
                    "keeper_bias": 0.18 + cycle * 0.008,
                    "match_state": 0,
                    "target_zone": "low-left",
                    "scored": 1 if cycle % 3 else 0,
                },
                {
                    "pressure": 0.71 + cycle * 0.012,
                    "footedness_code": cycle % 2,
                    "keeper_bias": 0.42 + cycle * 0.01,
                    "match_state": -1 if cycle % 2 else 0,
                    "target_zone": "high-right",
                    "scored": 0 if cycle % 3 else 1,
                },
                {
                    "pressure": 0.58 + cycle * 0.008,
                    "footedness_code": 0,
                    "keeper_bias": 0.24 + cycle * 0.009,
                    "match_state": 1 if cycle % 2 else -1,
                    "target_zone": "high-left",
                    "scored": 1 if cycle % 5 else 0,
                },
            ]
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    orchestrator = PipelineOrchestrator()

    def _run() -> None:
        artifact = train_penalty_models(synthetic_penalty_frame())
        print(artifact)

    orchestrator.execute(workflow_name="train_penalty_model", steps=[("train_penalty_model", _run)])
