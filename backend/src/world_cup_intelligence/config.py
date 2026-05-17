from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from world_cup_intelligence.core.settings import get_settings


def repo_root() -> Path:
    return get_settings().repo_root


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class TournamentConfig:
    slug: str
    name: str
    edition: str
    start_date: str
    end_date: str
    host_countries: list[str]
    host_cities: list[str]
    format: dict[str, Any]
    refresh_sources: dict[str, str]


@dataclass(frozen=True)
class CycleConfig:
    cycle_slug: str
    active_tournament: str
    refresh_jobs: dict[str, Any]


@lru_cache(maxsize=1)
def get_tournament_config() -> TournamentConfig:
    settings = get_settings()
    payload = load_yaml(repo_root() / "configs" / "tournaments" / f"{settings.active_tournament_slug}.yaml")
    payload["start_date"] = str(payload["start_date"])
    payload["end_date"] = str(payload["end_date"])
    return TournamentConfig(**payload)


@lru_cache(maxsize=1)
def get_cycle_config() -> CycleConfig:
    payload = load_yaml(repo_root() / "configs" / "cycles" / "men_2026.yaml")
    return CycleConfig(**payload)


def snapshot_path(*parts: str) -> Path:
    return get_settings().snapshot_dir.joinpath(*parts)


def artifact_path(filename: str) -> Path:
    target = get_settings().artifact_dir
    return target / filename


def metadata_path(*parts: str) -> Path:
    return get_settings().metadata_dir.joinpath(*parts)


def docs_path(*parts: str) -> Path:
    return get_settings().docs_dir.joinpath(*parts)
