from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from world_cup_intelligence.config import artifact_path
from world_cup_intelligence.core.logging import get_logger
from world_cup_intelligence.mlops.evaluation import EvaluationResult, evaluate_binary_classifier, evaluate_multiclass_classifier
from world_cup_intelligence.mlops.leakage import LeakageReport, inspect_supervised_frame
from world_cup_intelligence.mlops.splits import ClassificationSplit, build_classification_split
from world_cup_intelligence.mlops.tracking import log_json_artifact, log_metrics, log_params, start_run
from world_cup_intelligence.services.model_runtime import MATCH_FEATURES, PENALTY_FEATURES, XG_FEATURES
RANDOM_SEED = 2026

logger = get_logger(__name__)


@dataclass
class ModelArtifact:
    path: str
    version: str
    training_window: str
    sample_size: int


def _prefixed_metrics(prefix: str, metrics: dict[str, float]) -> dict[str, float]:
    return {f"{prefix}_{key}": value for key, value in metrics.items()}


def _safe_gap(left: dict[str, float], right: dict[str, float], key: str) -> float:
    if key not in left or key not in right:
        return 0.0
    return round(left[key] - right[key], 6)


def _extract_classes(model) -> list[Any]:
    if hasattr(model, "classes_"):
        return list(model.classes_)
    if hasattr(model, "named_steps") and "clf" in model.named_steps:
        return list(model.named_steps["clf"].classes_)
    raise AttributeError("Model does not expose classes_.")


def _evaluate_multiclass_model(name: str, model, x: pd.DataFrame, y: pd.Series) -> EvaluationResult:
    probabilities = model.predict_proba(x)
    predictions = model.predict(x)
    return evaluate_multiclass_classifier(name, y.tolist(), predictions.tolist(), probabilities, _extract_classes(model))


def _evaluate_binary_model(name: str, model, x: pd.DataFrame, y: pd.Series) -> EvaluationResult:
    probabilities = model.predict_proba(x)
    predictions = model.predict(x)
    return evaluate_binary_classifier(name, y.tolist(), predictions.tolist(), probabilities)


def _ranked_cv_results(search: GridSearchCV, *, limit: int = 5) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, params in enumerate(search.cv_results_["params"]):
        rows.append(
            {
                "rank": int(search.cv_results_["rank_test_score"][index]),
                "mean_test_score": round(float(search.cv_results_["mean_test_score"][index]), 6),
                "std_test_score": round(float(search.cv_results_["std_test_score"][index]), 6),
                "params": params,
            }
        )
    return sorted(rows, key=lambda row: row["rank"])[:limit]


def _fit_final_model(estimator, split: ClassificationSplit):
    final_model = clone(estimator)
    train_validation_x = pd.concat([split.train_x, split.validation_x], ignore_index=True)
    train_validation_y = pd.concat([split.train_y, split.validation_y], ignore_index=True)
    final_model.fit(train_validation_x, train_validation_y)
    return final_model


def _select_estimator(
    *,
    baseline_estimator,
    param_grid: dict[str, list[object]],
    split: ClassificationSplit,
    scoring: str,
    evaluator: Callable[[str, Any, pd.DataFrame, pd.Series], EvaluationResult],
) -> dict[str, object]:
    baseline_model = clone(baseline_estimator)
    baseline_model.fit(split.train_x, split.train_y)
    baseline_validation = evaluator("baseline_validation", baseline_model, split.validation_x, split.validation_y).metrics

    search = GridSearchCV(
        estimator=clone(baseline_estimator),
        param_grid=param_grid,
        scoring=scoring,
        cv=StratifiedKFold(n_splits=split.cv_folds, shuffle=True, random_state=split.random_seed),
        refit=True,
        n_jobs=1,
    )
    search.fit(split.train_x, split.train_y)
    tuned_model = search.best_estimator_
    tuned_validation = evaluator("tuned_validation", tuned_model, split.validation_x, split.validation_y).metrics

    if tuned_validation.get("macro_f1", 0.0) >= baseline_validation.get("macro_f1", 0.0):
        selected_kind = "tuned"
        selected_estimator = tuned_model
        selected_validation = tuned_validation
    else:
        selected_kind = "baseline"
        selected_estimator = baseline_model
        selected_validation = baseline_validation

    return {
        "selected_kind": selected_kind,
        "selected_estimator": selected_estimator,
        "selected_validation": selected_validation,
        "baseline_validation": baseline_validation,
        "best_params": search.best_params_,
        "best_cv_score": round(float(search.best_score_), 6),
        "cv_ranked_results": _ranked_cv_results(search),
    }


def _training_metadata(
    *,
    version: str,
    split: ClassificationSplit,
    metrics: dict[str, float],
    leakage_report: LeakageReport,
    selection: dict[str, object],
) -> dict[str, object]:
    return {
        "version": version,
        "split_sizes": split.split_sizes,
        "random_seed": split.random_seed,
        "cv_folds": split.cv_folds,
        "used_stratify": split.used_stratify,
        "metrics": metrics,
        "selected_model_kind": selection["selected_kind"],
        "best_params": selection["best_params"],
        "best_cv_score": selection["best_cv_score"],
        "cv_ranked_results": selection["cv_ranked_results"],
        "leakage_report": leakage_report.as_dict(),
    }


def _log_training_run(
    *,
    feature_columns: list[str],
    split: ClassificationSplit,
    leakage_report: LeakageReport,
    metrics: dict[str, float],
    metadata_name: str,
    metadata_payload: dict[str, object],
    extra_params: dict[str, object],
) -> None:
    log_params(
        {
            "feature_count": len(feature_columns),
            "sample_size": sum(split.split_sizes.values()),
            "cv_folds": split.cv_folds,
            "used_stratify": split.used_stratify,
            "duplicate_rows": leakage_report.duplicate_rows,
            "duplicate_feature_rows": leakage_report.duplicate_feature_rows,
            **extra_params,
        }
    )
    log_metrics(metrics)
    log_json_artifact(metadata_name, metadata_payload)


def _validate_leakage(frame: pd.DataFrame, feature_columns: list[str], target_column: str) -> LeakageReport:
    report = inspect_supervised_frame(frame, feature_columns, target_column)
    if report.leaked_feature_names:
        raise ValueError(f"Target leakage detected in feature set: {report.leaked_feature_names}")
    return report


def train_match_model(frame: pd.DataFrame) -> ModelArtifact:
    leakage_report = _validate_leakage(frame, MATCH_FEATURES, "label")
    split = build_classification_split(frame, MATCH_FEATURES, "label", random_seed=RANDOM_SEED)

    with start_run(
        experiment_suffix="match-model",
        run_name="train-match-logreg",
        tags={"pipeline": "training", "model_family": "logistic_regression"},
    ):
        estimator = Pipeline(
            steps=[
                ("scale", StandardScaler()),
                ("clf", LogisticRegression(max_iter=600, solver="lbfgs", random_state=RANDOM_SEED)),
            ]
        )
        selection = _select_estimator(
            baseline_estimator=estimator,
            param_grid={"clf__C": [0.25, 1.0, 4.0], "clf__class_weight": [None, "balanced"]},
            split=split,
            scoring="f1_macro",
            evaluator=_evaluate_multiclass_model,
        )
        final_model = _fit_final_model(selection["selected_estimator"], split)

        train_eval = _evaluate_multiclass_model("match_train", final_model, split.train_x, split.train_y)
        validation_eval = _evaluate_multiclass_model("match_validation", final_model, split.validation_x, split.validation_y)
        test_eval = _evaluate_multiclass_model("match_test", final_model, split.test_x, split.test_y)
        metrics = {
            **_prefixed_metrics("train", train_eval.metrics),
            **_prefixed_metrics("validation", validation_eval.metrics),
            **_prefixed_metrics("test", test_eval.metrics),
            "validation_macro_f1_gain_vs_baseline": round(
                selection["selected_validation"].get("macro_f1", 0.0)
                - selection["baseline_validation"].get("macro_f1", 0.0),
                6,
            ),
            "generalization_gap_macro_f1": _safe_gap(train_eval.metrics, test_eval.metrics, "macro_f1"),
            "generalization_gap_accuracy": _safe_gap(train_eval.metrics, test_eval.metrics, "accuracy"),
            "best_cv_score": float(selection["best_cv_score"]),
        }
        version = "match-logreg-v3"
        artifact = {
            "model": final_model,
            "version": version,
            "training_window": "last_10_years",
            "sample_size": int(len(frame)),
            "classes": _extract_classes(final_model),
            "metrics": metrics,
            "split_sizes": split.split_sizes,
            "random_seed": RANDOM_SEED,
            "selected_model_kind": selection["selected_kind"],
            "best_params": selection["best_params"],
            "leakage_report": leakage_report.as_dict(),
        }
        path = artifact_path("match_model.joblib")
        joblib.dump(artifact, path)
        metadata = _training_metadata(
            version=version,
            split=split,
            metrics=metrics,
            leakage_report=leakage_report,
            selection=selection,
        )
        _log_training_run(
            feature_columns=MATCH_FEATURES,
            split=split,
            leakage_report=leakage_report,
            metrics=metrics,
            metadata_name="match_model_metadata",
            metadata_payload=metadata,
            extra_params={"solver": "lbfgs", "selected_model_kind": selection["selected_kind"]},
        )
        logger.info("Trained match model with test_accuracy=%.4f", test_eval.metrics.get("accuracy", 0.0))
        return ModelArtifact(str(path), version, artifact["training_window"], artifact["sample_size"])


def train_xg_model(frame: pd.DataFrame) -> ModelArtifact:
    leakage_report = _validate_leakage(frame, XG_FEATURES, "is_goal")
    split = build_classification_split(frame, XG_FEATURES, "is_goal", random_seed=RANDOM_SEED)

    with start_run(
        experiment_suffix="xg-model",
        run_name="train-xg-gradient-boosting",
        tags={"pipeline": "training", "model_family": "xgboost"},
    ):
        estimator = XGBClassifier(
            n_estimators=60,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=RANDOM_SEED,
            n_jobs=1,
        )
        selection = _select_estimator(
            baseline_estimator=estimator,
            param_grid={"n_estimators": [40, 60], "max_depth": [3, 4], "learning_rate": [0.05, 0.08]},
            split=split,
            scoring="neg_log_loss",
            evaluator=_evaluate_binary_model,
        )
        final_model = _fit_final_model(selection["selected_estimator"], split)

        train_eval = _evaluate_binary_model("xg_train", final_model, split.train_x, split.train_y)
        validation_eval = _evaluate_binary_model("xg_validation", final_model, split.validation_x, split.validation_y)
        test_eval = _evaluate_binary_model("xg_test", final_model, split.test_x, split.test_y)
        metrics = {
            **_prefixed_metrics("train", train_eval.metrics),
            **_prefixed_metrics("validation", validation_eval.metrics),
            **_prefixed_metrics("test", test_eval.metrics),
            "validation_macro_f1_gain_vs_baseline": round(
                selection["selected_validation"].get("macro_f1", 0.0)
                - selection["baseline_validation"].get("macro_f1", 0.0),
                6,
            ),
            "generalization_gap_macro_f1": _safe_gap(train_eval.metrics, test_eval.metrics, "macro_f1"),
            "generalization_gap_accuracy": _safe_gap(train_eval.metrics, test_eval.metrics, "accuracy"),
            "best_cv_score": float(selection["best_cv_score"]),
        }
        version = "xg-xgboost-v3"
        artifact = {
            "model": final_model,
            "features": XG_FEATURES,
            "version": version,
            "training_window": "statsbomb_open_data_plus_world_cup",
            "sample_size": int(len(frame)),
            "metrics": metrics,
            "split_sizes": split.split_sizes,
            "random_seed": RANDOM_SEED,
            "selected_model_kind": selection["selected_kind"],
            "best_params": selection["best_params"],
            "leakage_report": leakage_report.as_dict(),
        }
        path = artifact_path("xg_model.joblib")
        joblib.dump(artifact, path)
        metadata = _training_metadata(
            version=version,
            split=split,
            metrics=metrics,
            leakage_report=leakage_report,
            selection=selection,
        )
        _log_training_run(
            feature_columns=XG_FEATURES,
            split=split,
            leakage_report=leakage_report,
            metrics=metrics,
            metadata_name="xg_model_metadata",
            metadata_payload=metadata,
            extra_params={"objective": "binary:logistic", "selected_model_kind": selection["selected_kind"]},
        )
        logger.info("Trained xG model with test_accuracy=%.4f", test_eval.metrics.get("accuracy", 0.0))
        return ModelArtifact(str(path), version, artifact["training_window"], artifact["sample_size"])


def train_penalty_models(frame: pd.DataFrame) -> ModelArtifact:
    leakage_report = _validate_leakage(frame, PENALTY_FEATURES, "target_zone")
    placement_frame = frame.copy()
    placement_encoder = LabelEncoder()
    placement_frame["target_zone_code"] = placement_encoder.fit_transform(placement_frame["target_zone"])
    placement_split = build_classification_split(placement_frame, PENALTY_FEATURES, "target_zone_code", random_seed=RANDOM_SEED)
    conversion_split = build_classification_split(frame, PENALTY_FEATURES, "scored", random_seed=RANDOM_SEED)

    with start_run(
        experiment_suffix="penalty-model",
        run_name="train-penalty-gradient-boosting",
        tags={"pipeline": "training", "model_family": "xgboost"},
    ):
        placement_estimator = XGBClassifier(
            n_estimators=50,
            max_depth=3,
            learning_rate=0.12,
            subsample=0.95,
            colsample_bytree=0.9,
            eval_metric="mlogloss",
            random_state=RANDOM_SEED,
            n_jobs=1,
        )
        conversion_estimator = XGBClassifier(
            n_estimators=50,
            max_depth=3,
            learning_rate=0.08,
            subsample=0.95,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=RANDOM_SEED,
            n_jobs=1,
        )
        placement_selection = _select_estimator(
            baseline_estimator=placement_estimator,
            param_grid={"n_estimators": [40, 50], "max_depth": [3, 4], "learning_rate": [0.08, 0.12]},
            split=placement_split,
            scoring="neg_log_loss",
            evaluator=_evaluate_multiclass_model,
        )
        conversion_selection = _select_estimator(
            baseline_estimator=conversion_estimator,
            param_grid={"n_estimators": [40, 50], "max_depth": [2, 3], "learning_rate": [0.05, 0.08]},
            split=conversion_split,
            scoring="neg_log_loss",
            evaluator=_evaluate_binary_model,
        )

        placement_model = _fit_final_model(placement_selection["selected_estimator"], placement_split)
        conversion_model = _fit_final_model(conversion_selection["selected_estimator"], conversion_split)

        placement_train = _evaluate_multiclass_model("penalty_placement_train", placement_model, placement_split.train_x, placement_split.train_y)
        placement_validation = _evaluate_multiclass_model(
            "penalty_placement_validation", placement_model, placement_split.validation_x, placement_split.validation_y
        )
        placement_test = _evaluate_multiclass_model("penalty_placement_test", placement_model, placement_split.test_x, placement_split.test_y)

        conversion_train = _evaluate_binary_model("penalty_conversion_train", conversion_model, conversion_split.train_x, conversion_split.train_y)
        conversion_validation = _evaluate_binary_model(
            "penalty_conversion_validation", conversion_model, conversion_split.validation_x, conversion_split.validation_y
        )
        conversion_test = _evaluate_binary_model("penalty_conversion_test", conversion_model, conversion_split.test_x, conversion_split.test_y)

        placement_class_labels = [
            str(label) for label in placement_encoder.inverse_transform(np.array(_extract_classes(placement_model), dtype=int))
        ]
        metrics = {
            **_prefixed_metrics("placement_train", placement_train.metrics),
            **_prefixed_metrics("placement_validation", placement_validation.metrics),
            **_prefixed_metrics("placement_test", placement_test.metrics),
            **_prefixed_metrics("conversion_train", conversion_train.metrics),
            **_prefixed_metrics("conversion_validation", conversion_validation.metrics),
            **_prefixed_metrics("conversion_test", conversion_test.metrics),
            "placement_validation_macro_f1_gain_vs_baseline": round(
                placement_selection["selected_validation"].get("macro_f1", 0.0)
                - placement_selection["baseline_validation"].get("macro_f1", 0.0),
                6,
            ),
            "conversion_validation_macro_f1_gain_vs_baseline": round(
                conversion_selection["selected_validation"].get("macro_f1", 0.0)
                - conversion_selection["baseline_validation"].get("macro_f1", 0.0),
                6,
            ),
            "placement_generalization_gap_macro_f1": _safe_gap(placement_train.metrics, placement_test.metrics, "macro_f1"),
            "conversion_generalization_gap_macro_f1": _safe_gap(conversion_train.metrics, conversion_test.metrics, "macro_f1"),
            "placement_best_cv_score": float(placement_selection["best_cv_score"]),
            "conversion_best_cv_score": float(conversion_selection["best_cv_score"]),
        }

        version = "penalty-xgboost-v3"
        artifact = {
            "placement_model": placement_model,
            "conversion_model": conversion_model,
            "features": PENALTY_FEATURES,
            "version": version,
            "training_window": "major_tournaments_open_data",
            "sample_size": int(len(frame)),
            "metrics": metrics,
            "placement_classes": placement_class_labels,
            "placement_label_mapping": {
                int(code): str(label) for code, label in enumerate(placement_encoder.classes_)
            },
            "split_sizes": {
                "placement": placement_split.split_sizes,
                "conversion": conversion_split.split_sizes,
            },
            "random_seed": RANDOM_SEED,
            "best_params": {
                "placement": placement_selection["best_params"],
                "conversion": conversion_selection["best_params"],
            },
            "selected_model_kind": {
                "placement": placement_selection["selected_kind"],
                "conversion": conversion_selection["selected_kind"],
            },
            "leakage_report": leakage_report.as_dict(),
        }
        path = artifact_path("penalty_model.joblib")
        joblib.dump(artifact, path)
        metadata = {
            "version": version,
            "metrics": metrics,
            "placement": _training_metadata(
                version=version,
                split=placement_split,
                metrics=metrics,
                leakage_report=leakage_report,
                selection=placement_selection,
            ),
            "conversion": _training_metadata(
                version=version,
                split=conversion_split,
                metrics=metrics,
                leakage_report=leakage_report,
                selection=conversion_selection,
            ),
        }
        log_params(
            {
                "feature_count": len(PENALTY_FEATURES),
                "sample_size": len(frame),
                "placement_cv_folds": placement_split.cv_folds,
                "conversion_cv_folds": conversion_split.cv_folds,
                "duplicate_rows": leakage_report.duplicate_rows,
                "duplicate_feature_rows": leakage_report.duplicate_feature_rows,
            }
        )
        log_metrics(metrics)
        log_json_artifact("penalty_model_metadata", metadata)
        logger.info("Trained penalty models with conversion_test_accuracy=%.4f", conversion_test.metrics.get("accuracy", 0.0))
        return ModelArtifact(str(path), version, artifact["training_window"], artifact["sample_size"])


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
