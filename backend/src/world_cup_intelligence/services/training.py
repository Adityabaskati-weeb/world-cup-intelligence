from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from world_cup_intelligence.config import artifact_path


MATCH_FEATURES = [
    "elo_diff",
    "form_diff",
    "goal_diff_trend",
    "rest_days_diff",
    "confederation_gap",
    "host_flag",
]


@dataclass
class ModelArtifact:
    path: str
    version: str
    training_window: str
    sample_size: int


def train_match_model(frame: pd.DataFrame) -> ModelArtifact:
    model = Pipeline(
        steps=[
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(max_iter=400, solver="lbfgs")),
        ]
    )
    model.fit(frame[MATCH_FEATURES], frame["label"])
    artifact = {
        "model": model,
        "version": "match-logreg-v1",
        "training_window": "last_10_years",
        "sample_size": int(len(frame)),
        "classes": list(model.named_steps["clf"].classes_),
    }
    path = artifact_path("match_model.joblib")
    joblib.dump(artifact, path)
    return ModelArtifact(str(path), artifact["version"], artifact["training_window"], artifact["sample_size"])


def train_xg_model(frame: pd.DataFrame) -> ModelArtifact:
    features = ["distance", "angle", "minute", "pressure", "game_state", "body_part_code", "shot_type_code"]
    model = XGBClassifier(
        n_estimators=50,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
    )
    model.fit(frame[features], frame["is_goal"])
    artifact = {
        "model": model,
        "features": features,
        "version": "xg-xgboost-v1",
        "training_window": "statsbomb_open_data_plus_world_cup",
        "sample_size": int(len(frame)),
    }
    path = artifact_path("xg_model.joblib")
    joblib.dump(artifact, path)
    return ModelArtifact(str(path), artifact["version"], artifact["training_window"], artifact["sample_size"])


def train_penalty_models(frame: pd.DataFrame) -> ModelArtifact:
    zone_features = ["pressure", "footedness_code", "keeper_bias", "match_state"]
    placement = XGBClassifier(
        n_estimators=40,
        max_depth=3,
        learning_rate=0.12,
        subsample=0.95,
        colsample_bytree=0.9,
        eval_metric="mlogloss",
    )
    conversion = XGBClassifier(
        n_estimators=40,
        max_depth=3,
        learning_rate=0.1,
        subsample=0.95,
        colsample_bytree=0.9,
        eval_metric="logloss",
    )
    placement.fit(frame[zone_features], frame["target_zone"])
    conversion.fit(frame[zone_features], frame["scored"])
    artifact = {
        "placement_model": placement,
        "conversion_model": conversion,
        "features": zone_features,
        "version": "penalty-xgboost-v1",
        "training_window": "major_tournaments_open_data",
        "sample_size": int(len(frame)),
    }
    path = artifact_path("penalty_model.joblib")
    joblib.dump(artifact, path)
    return ModelArtifact(str(path), artifact["version"], artifact["training_window"], artifact["sample_size"])


def load_artifact(filename: str) -> dict[str, Any] | None:
    path = artifact_path(filename)
    if not path.exists():
        return None
    return joblib.load(path)


def softmax(values: list[float]) -> list[float]:
    array = np.array(values, dtype=float)
    shifted = array - array.max()
    exp = np.exp(shifted)
    result = exp / exp.sum()
    return [float(value) for value in result]
