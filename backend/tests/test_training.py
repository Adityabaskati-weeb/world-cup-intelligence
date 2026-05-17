import pandas as pd

from world_cup_intelligence.services.training import load_artifact, train_match_model, train_penalty_models, train_xg_model


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


def test_match_training_logs_split_metrics() -> None:
    artifact = train_match_model(synthetic_match_frame())
    payload = load_artifact("match_model.joblib")
    assert payload is not None
    assert artifact.version == "match-logreg-v3"
    assert payload["split_sizes"]["train"] + payload["split_sizes"]["validation"] + payload["split_sizes"]["test"] == payload["sample_size"]
    assert "test_accuracy" in payload["metrics"]
    assert "best_params" in payload


def test_xg_training_logs_generalization_metrics() -> None:
    artifact = train_xg_model(synthetic_xg_frame())
    payload = load_artifact("xg_model.joblib")
    assert payload is not None
    assert artifact.version == "xg-gradientboost-v4"
    assert "generalization_gap_macro_f1" in payload["metrics"]
    assert payload["split_sizes"]["test"] > 0


def test_penalty_training_persists_dual_model_metadata() -> None:
    artifact = train_penalty_models(synthetic_penalty_frame())
    payload = load_artifact("penalty_model.joblib")
    assert payload is not None
    assert artifact.version == "penalty-gradientboost-v4"
    assert "placement" in payload["best_params"]
    assert "conversion" in payload["best_params"]
    assert "placement_test_accuracy" in payload["metrics"]
    assert "conversion_test_accuracy" in payload["metrics"]
