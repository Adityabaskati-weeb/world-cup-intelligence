from __future__ import annotations

import pandas as pd

from world_cup_intelligence.services.training import train_match_model


def synthetic_match_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"elo_diff": 120, "form_diff": 1.5, "goal_diff_trend": 1.2, "rest_days_diff": 2, "confederation_gap": 1, "host_flag": 1, "label": "home"},
            {"elo_diff": -90, "form_diff": -1.2, "goal_diff_trend": -0.7, "rest_days_diff": -1, "confederation_gap": -1, "host_flag": 0, "label": "away"},
            {"elo_diff": 10, "form_diff": 0.2, "goal_diff_trend": 0.1, "rest_days_diff": 0, "confederation_gap": 0, "host_flag": 0, "label": "draw"},
            {"elo_diff": 65, "form_diff": 0.7, "goal_diff_trend": 0.5, "rest_days_diff": 1, "confederation_gap": 0, "host_flag": 0, "label": "home"},
            {"elo_diff": -40, "form_diff": -0.6, "goal_diff_trend": -0.3, "rest_days_diff": 0, "confederation_gap": -1, "host_flag": 0, "label": "away"},
            {"elo_diff": 5, "form_diff": 0.1, "goal_diff_trend": -0.1, "rest_days_diff": 0, "confederation_gap": 0, "host_flag": 0, "label": "draw"},
        ]
    )


if __name__ == "__main__":
    artifact = train_match_model(synthetic_match_frame())
    print(artifact)

