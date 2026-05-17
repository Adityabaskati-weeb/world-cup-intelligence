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
from world_cup_intelligence.core.logging import get_logger
from world_cup_intelligence.mlops.evaluation import evaluate_binary_classifier, evaluate_multiclass_classifier
from world_cup_intelligence.mlops.tracking import log_json_artifact, log_metrics, log_params, start_run


MATCH_FEATURES = [
    "elo_diff",
    "form_diff",
    "goal_diff_trend",
    "rest_days_diff",
    "confederation_gap",
    "host_flag",
]

logger = get_logger(__name__)


@dataclass
class ModelArtifact:
    path: str
    version: str
    training_window: str
    sample_size: int


def train_match_model(frame: pd.DataFrame) -> ModelArtifact:
    with start_run(
        experiment_suffix="match-model",
        run_name="train-match-logreg",
        tags={"pipeline": "training", "model_family": "logistic_regression"},
    ):
        model = Pipeline(
            steps=[
                ("scale", StandardScaler()),
                ("clf", LogisticRegression(max_iter=400, solver="lbfgs")),
            ]
        )
        model.fit(frame[MATCH_FEATURES], frame["label"])
        probabilities = model.predict_proba(frame[MATCH_FEATURES])
        predictions = model.predict(frame[MATCH_FEATURES])
        classes = list(model.named_steps["clf"].classes_)
        evaluation = evaluate_multiclass_classifier("match", frame["label"].tolist(), predictions.tolist(), probabilities, classes)

        artifact = {
            "model": model,
            "version": "match-logreg-v2",
            "training_window": "last_10_years",
            "sample_size": int(len(frame)),
            "classes": classes,
            "metrics": evaluation.metrics,
        }
        path = artifact_path("match_model.joblib")
        joblib.dump(artifact, path)
        log_params({"feature_count": len(MATCH_FEATURES), "sample_size": len(frame), "solver": "lbfgs"})
        log_metrics(evaluation.metrics)
        log_json_artifact("match_model_metadata", {"version": artifact["version"], "metrics": evaluation.metrics})
        logger.info("Trained match model with accuracy=%.4f", evaluation.metrics.get("accuracy", 0.0))
        return ModelArtifact(str(path), artifact["version"], artifact["training_window"], artifact["sample_size"])


def train_xg_model(frame: pd.DataFrame) -> ModelArtifact:
    features = ["distance", "angle", "minute", "pressure", "game_state", "body_part_code", "shot_type_code"]
    with start_run(
        experiment_suffix="xg-model",
        run_name="train-xg-gradient-boosting",
        tags={"pipeline": "training", "model_family": "xgboost"},
    ):
        model = XGBClassifier(
            n_estimators=50,
            max_depth=4,
            learning_rate=0.1,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
        )
        model.fit(frame[features], frame["is_goal"])
        probabilities = model.predict_proba(frame[features])
        predictions = model.predict(frame[features])
        evaluation = evaluate_binary_classifier("xg", frame["is_goal"].tolist(), predictions.tolist(), probabilities)
        artifact = {
            "model": model,
            "features": features,
            "version": "xg-xgboost-v2",
            "training_window": "statsbomb_open_data_plus_world_cup",
            "sample_size": int(len(frame)),
            "metrics": evaluation.metrics,
        }
        path = artifact_path("xg_model.joblib")
        joblib.dump(artifact, path)
        log_params({"feature_count": len(features), "sample_size": len(frame), "n_estimators": 50})
        log_metrics(evaluation.metrics)
        log_json_artifact("xg_model_metadata", {"version": artifact["version"], "metrics": evaluation.metrics})
        logger.info("Trained xG model with accuracy=%.4f", evaluation.metrics.get("accuracy", 0.0))
        return ModelArtifact(str(path), artifact["version"], artifact["training_window"], artifact["sample_size"])


def train_penalty_models(frame: pd.DataFrame) -> ModelArtifact:
    zone_features = ["pressure", "footedness_code", "keeper_bias", "match_state"]
    with start_run(
        experiment_suffix="penalty-model",
        run_name="train-penalty-gradient-boosting",
        tags={"pipeline": "training", "model_family": "xgboost"},
    ):
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

        placement_probabilities = placement.predict_proba(frame[zone_features])
        placement_predictions = placement.predict(frame[zone_features])
        placement_classes = list(placement.classes_)
        placement_eval = evaluate_multiclass_classifier(
            "penalty_placement",
            frame["target_zone"].tolist(),
            placement_predictions.tolist(),
            placement_probabilities,
            placement_classes,
        )

        conversion_probabilities = conversion.predict_proba(frame[zone_features])
        conversion_predictions = conversion.predict(frame[zone_features])
        conversion_eval = evaluate_binary_classifier(
            "penalty_conversion",
            frame["scored"].tolist(),
            conversion_predictions.tolist(),
            conversion_probabilities,
        )

        metrics = {
            **{f"placement_{key}": value for key, value in placement_eval.metrics.items()},
            **{f"conversion_{key}": value for key, value in conversion_eval.metrics.items()},
        }
        artifact = {
            "placement_model": placement,
            "conversion_model": conversion,
            "features": zone_features,
            "version": "penalty-xgboost-v2",
            "training_window": "major_tournaments_open_data",
            "sample_size": int(len(frame)),
            "metrics": metrics,
        }
        path = artifact_path("penalty_model.joblib")
        joblib.dump(artifact, path)
        log_params({"feature_count": len(zone_features), "sample_size": len(frame), "placement_estimators": 40})
        log_metrics(metrics)
        log_json_artifact("penalty_model_metadata", {"version": artifact["version"], "metrics": metrics})
        logger.info("Trained penalty models with conversion_accuracy=%.4f", metrics.get("conversion_accuracy", 0.0))
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
