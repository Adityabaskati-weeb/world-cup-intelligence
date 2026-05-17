from __future__ import annotations

import json
from urllib.parse import urlparse

from world_cup_intelligence.config import get_cycle_config, get_tournament_config, metadata_path
from world_cup_intelligence.core.monitoring import request_monitor
from world_cup_intelligence.core.settings import get_settings
from world_cup_intelligence.schemas.api import (
    EndpointMetric,
    ModelOverview,
    RequestMetrics,
    RuntimeOverview,
    SystemOverviewResponse,
    WorkflowOverview,
)
from world_cup_intelligence.services.model_runtime import load_artifact


def runtime_mode_label(use_snapshot_data: bool) -> str:
    return "snapshot_backed_api" if use_snapshot_data else "live_api"


def _tracking_backend_label(tracking_uri: str) -> str:
    parsed = urlparse(tracking_uri)
    if tracking_uri.startswith("sqlite:///"):
        return "sqlite"
    if parsed.scheme == "file":
        return "file"
    return parsed.scheme or "file"


class SystemOverviewService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _workflow_runs(self) -> list[dict[str, object]]:
        path = metadata_path("workflow_state.json")
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        return list(payload.get("runs", []))

    def _workflow_overview(self) -> list[WorkflowOverview]:
        latest_by_name: dict[str, dict[str, object]] = {}
        for run in self._workflow_runs():
            workflow_name = str(run.get("workflow_name", "unknown"))
            latest_by_name[workflow_name] = run

        ordered_names = ["refresh_all", "train_match_model", "train_xg_model", "train_penalty_model"]
        overviews: list[WorkflowOverview] = []
        for workflow_name in ordered_names:
            run = latest_by_name.get(workflow_name)
            if not run:
                continue
            steps = list(run.get("steps", []))
            overviews.append(
                WorkflowOverview(
                    workflow_name=workflow_name,
                    status=str(run.get("status", "unknown")),
                    finished_at=str(run.get("finished_at")) if run.get("finished_at") else None,
                    step_count=len(steps),
                )
            )
        return overviews

    def _model_overview(self, slug: str, filename: str) -> ModelOverview | None:
        artifact = load_artifact(filename)
        if not artifact:
            return None

        metrics = artifact.get("metrics", {})
        selected_model_kind = artifact.get("selected_model_kind")
        if isinstance(selected_model_kind, dict):
            selected_model_kind = ", ".join(f"{key}:{value}" for key, value in selected_model_kind.items())

        return ModelOverview(
            slug=slug,
            version=str(artifact.get("version", "unknown")),
            training_window=str(artifact.get("training_window", "unknown")),
            sample_size=int(artifact.get("sample_size", 0)),
            selected_model_kind=str(selected_model_kind) if selected_model_kind else None,
            test_accuracy=_metric_value(metrics, "test_accuracy", "conversion_test_accuracy"),
            test_macro_f1=_metric_value(metrics, "test_macro_f1", "conversion_test_macro_f1"),
            validation_macro_f1=_metric_value(metrics, "validation_macro_f1", "conversion_validation_macro_f1"),
            generalization_gap=_metric_value(
                metrics,
                "generalization_gap_macro_f1",
                "conversion_generalization_gap_macro_f1",
            ),
        )

    def _models(self) -> list[ModelOverview]:
        models = [
            self._model_overview("match", "match_model.joblib"),
            self._model_overview("xg", "xg_model.joblib"),
            self._model_overview("penalty", "penalty_model.joblib"),
        ]
        return [model for model in models if model is not None]

    def _runtime_overview(self) -> RuntimeOverview:
        tournament = get_tournament_config()
        return RuntimeOverview(
            mode=runtime_mode_label(self.settings.use_demo_data),
            use_demo_data=self.settings.use_demo_data,
            active_tournament=tournament.slug,
            runtime_root=str(self.settings.runtime_root),
            tracking_backend=_tracking_backend_label(self.settings.mlflow_tracking_uri),
        )

    def _request_metrics(self) -> RequestMetrics:
        snapshot = request_monitor.snapshot()
        return RequestMetrics(
            total_requests=int(snapshot["total_requests"]),
            error_requests=int(snapshot["error_requests"]),
            uptime_seconds=float(snapshot["uptime_seconds"]),
            top_paths=[EndpointMetric(**path) for path in snapshot["top_paths"]],
        )

    def overview(self) -> SystemOverviewResponse:
        # Access cycle config to keep this endpoint sensitive to broken config changes.
        get_cycle_config()
        return SystemOverviewResponse(
            runtime=self._runtime_overview(),
            models=self._models(),
            workflows=self._workflow_overview(),
            request_metrics=self._request_metrics(),
        )


def _metric_value(metrics: object, *keys: str) -> float | None:
    if not isinstance(metrics, dict):
        return None
    for key in keys:
        value = metrics.get(key)
        if value is not None:
            return round(float(value), 6)
    return None
