from __future__ import annotations

from typing import Any

import joblib

from world_cup_intelligence.config import artifact_path
from world_cup_intelligence.core.logging import get_logger


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

logger = get_logger(__name__)


def load_artifact(filename: str) -> dict[str, Any] | None:
    path = artifact_path(filename)
    if not path.exists():
        return None
    try:
        return joblib.load(path)
    except Exception:
        logger.warning("Could not load model artifact %s from %s", filename, path, exc_info=True)
        return None
