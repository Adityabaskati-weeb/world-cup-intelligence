from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse


def _env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppSettings:
    project_name: str
    active_tournament_slug: str
    repo_root: Path
    runtime_root: Path
    data_dir: Path
    snapshot_dir: Path
    metadata_dir: Path
    artifact_dir: Path
    docs_dir: Path
    mlflow_tracking_uri: str
    mlflow_experiment_prefix: str
    log_level: str
    soccerdata_dir: Path
    use_demo_data: bool


def _resolve_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _env_value(name: str) -> str | None:
    raw = os.getenv(name)
    if raw is None:
        return None
    value = raw.strip()
    return value or None


def _normalize_tracking_uri(raw_uri: str) -> str:
    parsed = urlparse(raw_uri)
    if len(parsed.scheme) == 1 and raw_uri[1:3] in {":\\", ":/"}:
        return Path(raw_uri).resolve().as_uri()
    if parsed.scheme:
        return raw_uri
    return Path(raw_uri).resolve().as_uri()


def _resolve_runtime_root(repo: Path) -> Path:
    candidates: list[Path] = []
    explicit_runtime = _env_value("WCI_RUNTIME_DIR")
    if explicit_runtime:
        candidates.append(Path(explicit_runtime))

    local_app_data = _env_value("LOCALAPPDATA")
    if local_app_data:
        candidates.append(Path(local_app_data) / "world-cup-intelligence")

    candidates.append(repo / ".runtime")

    last_error: OSError | None = None
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError as exc:
            last_error = exc

    if last_error is not None:
        raise last_error
    raise RuntimeError("Unable to resolve a writable runtime directory.")


def _default_tracking_uri(repo: Path, runtime_root: Path, mlruns_dir: Path) -> str:
    if runtime_root.is_relative_to(repo):
        return mlruns_dir.resolve().as_uri()
    return f"sqlite:///{(mlruns_dir / 'mlflow.db').resolve().as_posix()}"


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    repo = _resolve_repo_root()
    runtime_root = _resolve_runtime_root(repo)
    data_dir = repo / "data"
    snapshot_dir = data_dir / "snapshots"
    metadata_dir = data_dir / "metadata"
    artifact_dir = repo / "backend" / "artifacts"
    docs_dir = repo / "docs"
    soccerdata_dir = Path(os.getenv("SOCCERDATA_DIR", str(repo / ".soccerdata-cache")))
    mlruns_dir = runtime_root / "mlruns"
    os.environ.setdefault("SOCCERDATA_DIR", str(soccerdata_dir))

    for path in (data_dir, snapshot_dir, metadata_dir, artifact_dir, docs_dir, soccerdata_dir, mlruns_dir):
        path.mkdir(parents=True, exist_ok=True)

    default_tracking_uri = _default_tracking_uri(repo=repo, runtime_root=runtime_root, mlruns_dir=mlruns_dir)

    return AppSettings(
        project_name=os.getenv("WCI_PROJECT_NAME", "World Cup Intelligence 2026"),
        active_tournament_slug=os.getenv("WCI_ACTIVE_TOURNAMENT", "world_cup_2026"),
        repo_root=repo,
        runtime_root=runtime_root,
        data_dir=data_dir,
        snapshot_dir=snapshot_dir,
        metadata_dir=metadata_dir,
        artifact_dir=artifact_dir,
        docs_dir=docs_dir,
        mlflow_tracking_uri=_normalize_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", default_tracking_uri)),
        mlflow_experiment_prefix=os.getenv("WCI_MLFLOW_EXPERIMENT_PREFIX", "world-cup-intelligence"),
        log_level=os.getenv("WCI_LOG_LEVEL", "INFO").upper(),
        soccerdata_dir=soccerdata_dir,
        use_demo_data=_env_flag("WCI_USE_DEMO_DATA", True),
    )
