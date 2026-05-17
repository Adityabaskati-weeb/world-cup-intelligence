from world_cup_intelligence.config import artifact_path
from world_cup_intelligence.services.training import train_match_model, train_penalty_models, train_xg_model
import pandas as pd


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


def test_training_smoke_creates_artifacts() -> None:
    train_match_model(synthetic_match_frame())
    train_xg_model(synthetic_xg_frame())
    train_penalty_models(synthetic_penalty_frame())

    assert artifact_path("match_model.joblib").exists()
    assert artifact_path("xg_model.joblib").exists()
    assert artifact_path("penalty_model.joblib").exists()

