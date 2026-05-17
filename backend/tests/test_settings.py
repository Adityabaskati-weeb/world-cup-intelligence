from world_cup_intelligence.core.settings import get_settings


def test_settings_resolve_project_paths() -> None:
    settings = get_settings()
    assert settings.active_tournament_slug == "world_cup_2026"
    assert settings.runtime_root.exists()
    assert settings.mlflow_tracking_uri.startswith(("file:", "sqlite:"))
    assert settings.snapshot_dir.exists()
    assert settings.metadata_dir.exists()
    assert settings.artifact_dir.exists()
