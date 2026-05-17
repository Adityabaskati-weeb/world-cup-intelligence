from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import mlflow

from world_cup_intelligence.core.logging import get_logger
from world_cup_intelligence.core.settings import get_settings


logger = get_logger(__name__)


def _configure_tracking() -> None:
    settings = get_settings()
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)


def experiment_name(suffix: str) -> str:
    settings = get_settings()
    return f"{settings.mlflow_experiment_prefix}-{suffix}"


@contextmanager
def start_run(experiment_suffix: str, run_name: str, tags: dict[str, str] | None = None) -> Iterator[None]:
    _configure_tracking()
    mlflow.set_experiment(experiment_name(experiment_suffix))
    with mlflow.start_run(run_name=run_name):
        if tags:
            mlflow.set_tags(tags)
        yield


def log_params(params: dict[str, object]) -> None:
    serializable = {key: value for key, value in params.items() if value is not None}
    if serializable:
        mlflow.log_params(serializable)


def log_metrics(metrics: dict[str, float]) -> None:
    if metrics:
        mlflow.log_metrics(metrics)


def log_json_artifact(name: str, payload: dict[str, object]) -> None:
    target = Path(get_settings().artifact_dir) / f"{name}.json"
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    mlflow.log_artifact(str(target))
    logger.info("Logged artifact %s", target.name)
