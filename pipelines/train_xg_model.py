from __future__ import annotations

import pandas as pd

from world_cup_intelligence.services.training import train_xg_model


def synthetic_xg_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"distance": 9.5, "angle": 0.65, "minute": 18, "pressure": 0.15, "game_state": 0, "body_part_code": 1, "shot_type_code": 0, "is_goal": 1},
            {"distance": 17.0, "angle": 0.30, "minute": 71, "pressure": 0.55, "game_state": 1, "body_part_code": 2, "shot_type_code": 1, "is_goal": 0},
            {"distance": 13.0, "angle": 0.50, "minute": 42, "pressure": 0.22, "game_state": 0, "body_part_code": 1, "shot_type_code": 0, "is_goal": 1},
            {"distance": 22.0, "angle": 0.18, "minute": 83, "pressure": 0.60, "game_state": -1, "body_part_code": 0, "shot_type_code": 2, "is_goal": 0},
            {"distance": 7.0, "angle": 0.72, "minute": 54, "pressure": 0.10, "game_state": 0, "body_part_code": 1, "shot_type_code": 0, "is_goal": 1},
            {"distance": 19.5, "angle": 0.24, "minute": 63, "pressure": 0.35, "game_state": 1, "body_part_code": 0, "shot_type_code": 1, "is_goal": 0},
        ]
    )


if __name__ == "__main__":
    artifact = train_xg_model(synthetic_xg_frame())
    print(artifact)

