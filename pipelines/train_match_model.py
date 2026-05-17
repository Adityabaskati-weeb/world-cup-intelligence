from __future__ import annotations

import pandas as pd

from world_cup_intelligence.orchestration.workflows import PipelineOrchestrator
from world_cup_intelligence.services.training import train_match_model


def synthetic_match_frame() -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for cycle in range(8):
        rows.extend(
            [
                {
                    "elo_diff": 120 - cycle * 4,
                    "form_diff": 1.6 - cycle * 0.05,
                    "goal_diff_trend": 1.3 - cycle * 0.03,
                    "rest_days_diff": 2 - (cycle % 2),
                    "confederation_gap": 1,
                    "host_flag": 1 if cycle < 3 else 0,
                    "label": "home",
                },
                {
                    "elo_diff": -95 + cycle * 5,
                    "form_diff": -1.3 + cycle * 0.04,
                    "goal_diff_trend": -0.8 + cycle * 0.02,
                    "rest_days_diff": -1 + (cycle % 2),
                    "confederation_gap": -1,
                    "host_flag": 0,
                    "label": "away",
                },
                {
                    "elo_diff": -6 + cycle * 2,
                    "form_diff": -0.15 + cycle * 0.04,
                    "goal_diff_trend": -0.2 + cycle * 0.05,
                    "rest_days_diff": 0,
                    "confederation_gap": 0,
                    "host_flag": 0,
                    "label": "draw",
                },
            ]
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    orchestrator = PipelineOrchestrator()

    def _run() -> None:
        artifact = train_match_model(synthetic_match_frame())
        print(artifact)

    orchestrator.execute(workflow_name="train_match_model", steps=[("train_match_model", _run)])
