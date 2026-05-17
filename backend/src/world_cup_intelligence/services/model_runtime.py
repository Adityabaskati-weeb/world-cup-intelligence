from __future__ import annotations

from typing import Any

import joblib

from world_cup_intelligence.config import artifact_path


MATCH_FEATURES = [
    "elo_diff",
    "form_diff",
    "goal_diff_trend",
    "rest_days_diff",
    "confederation_gap",
    "host_flag",
]
XG_FEATURES = ["distance", "angle", "minute", "pressure", "game_state", "body_part_code", "shot_type_code"]
PENALTY_FEATURES = ["pressure", "footedness_code", "keeper_bias", "match_state"]


def load_artifact(filename: str) -> dict[str, Any] | None:
    path = artifact_path(filename)
    if not path.exists():
        return None
    return joblib.load(path)

