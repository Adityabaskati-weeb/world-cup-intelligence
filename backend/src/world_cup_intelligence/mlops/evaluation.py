from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, brier_score_loss, f1_score, log_loss, precision_score, recall_score, roc_auc_score


@dataclass(frozen=True)
class EvaluationResult:
    name: str
    metrics: dict[str, float]


def _safe_metric(metrics: dict[str, float], key: str, value: float | None) -> None:
    if value is None:
        return
    metrics[key] = round(float(value), 6)


def evaluate_multiclass_classifier(
    name: str,
    y_true: list[Any],
    y_pred: list[Any],
    probabilities: np.ndarray,
    labels: list[Any],
) -> EvaluationResult:
    metrics: dict[str, float] = {}
    _safe_metric(metrics, "accuracy", accuracy_score(y_true, y_pred))
    _safe_metric(metrics, "macro_f1", f1_score(y_true, y_pred, average="macro"))
    _safe_metric(metrics, "macro_precision", precision_score(y_true, y_pred, average="macro", zero_division=0))
    _safe_metric(metrics, "macro_recall", recall_score(y_true, y_pred, average="macro", zero_division=0))
    _safe_metric(metrics, "log_loss", log_loss(y_true, probabilities, labels=labels))
    return EvaluationResult(name=name, metrics=metrics)


def evaluate_binary_classifier(
    name: str,
    y_true: list[Any],
    y_pred: list[Any],
    probabilities: np.ndarray,
) -> EvaluationResult:
    metrics: dict[str, float] = {}
    _safe_metric(metrics, "accuracy", accuracy_score(y_true, y_pred))
    _safe_metric(metrics, "macro_f1", f1_score(y_true, y_pred, average="macro"))
    _safe_metric(metrics, "macro_precision", precision_score(y_true, y_pred, average="macro", zero_division=0))
    _safe_metric(metrics, "macro_recall", recall_score(y_true, y_pred, average="macro", zero_division=0))
    _safe_metric(metrics, "log_loss", log_loss(y_true, probabilities))

    roc_auc: float | None = None
    labels = sorted(set(y_true))
    if len(labels) == 2:
        positive_index = 1 if probabilities.shape[1] > 1 else 0
        roc_auc = roc_auc_score(y_true, probabilities[:, positive_index])
        _safe_metric(metrics, "brier_score", brier_score_loss(y_true, probabilities[:, positive_index]))
    _safe_metric(metrics, "roc_auc", roc_auc)
    return EvaluationResult(name=name, metrics=metrics)
