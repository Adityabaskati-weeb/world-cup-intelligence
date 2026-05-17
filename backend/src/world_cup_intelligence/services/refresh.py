from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from world_cup_intelligence.config import get_cycle_config, get_tournament_config, snapshot_path
from world_cup_intelligence.data.repository import SnapshotRepository
from world_cup_intelligence.schemas.api import RefreshSourceStatus, RefreshStatusResponse


class RefreshStatusService:
    def __init__(self, repository: SnapshotRepository) -> None:
        self.repository = repository

    @staticmethod
    def _file_timestamp(path: Path) -> str:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(timespec="minutes").replace("+00:00", "Z")

    @staticmethod
    def _payload_timestamp(payload: dict[str, Any], path: Path) -> str:
        updated_at = payload.get("updated_at")
        if isinstance(updated_at, str) and updated_at.strip():
            return updated_at
        return RefreshStatusService._file_timestamp(path)

    def _tournament_source(self) -> RefreshSourceStatus:
        tournament_config = get_tournament_config()
        path = snapshot_path("tournaments", f"{tournament_config.slug}.json")
        payload = self.repository.tournament_snapshot()
        fixture_count = len(payload.get("fixtures", []))
        group_count = len(payload.get("groups", {}))
        return RefreshSourceStatus(
            key="tournament_reference",
            label="Tournament reference",
            status="snapshot",
            updated_at=self._payload_timestamp(payload, path),
            source="FIFA + config snapshot",
            detail=(
                f"{group_count} groups and {fixture_count} fixtures are cached from the 2026 tournament reference layer."
            ),
        )

    def _fixture_sync_source(self) -> RefreshSourceStatus:
        cycle_config = get_cycle_config()
        path = snapshot_path("football_data_snapshot.json")
        payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        status = str(payload.get("status", "unavailable"))
        matches = payload.get("matches", [])
        cadence = cycle_config.refresh_jobs.get("tournament_sync", {}).get("cadence", "scheduled")
        if status in {"ok", "available", "ready", "live"}:
            return RefreshSourceStatus(
                key="fixture_sync",
                label="Fixture sync",
                status="live",
                updated_at=self._payload_timestamp(payload, path),
                source="football-data.org",
                detail=f"{len(matches)} fixture rows are synced through the API cadence ({cadence}) during the tournament window.",
            )

        reason = str(payload.get("reason", "The football-data.org feed is not configured yet."))
        return RefreshSourceStatus(
            key="fixture_sync",
            label="Fixture sync",
            status="attention",
            updated_at=self._file_timestamp(path) if path.exists() else None,
            source="football-data.org API",
            detail=f"{reason} Automatic sync is designed for {cadence} refreshes during the tournament window.",
        )

    def _xg_source(self) -> RefreshSourceStatus:
        path = snapshot_path("players", "xg_profiles.json")
        payload = self.repository.xg_profiles()
        teams = payload.get("teams", [])
        players = payload.get("players", [])
        shots = sum(len(team.get("shots", [])) for team in teams)
        return RefreshSourceStatus(
            key="xg_intelligence",
            label="xG intelligence",
            status="snapshot",
            updated_at=self._payload_timestamp(payload, path),
            source="StatsBomb open-data snapshot",
            detail=f"{len(teams)} tracked teams, {len(players)} explicit player profiles, and {shots} shot events power the xG layer.",
        )

    def _penalty_source(self) -> RefreshSourceStatus:
        path = snapshot_path("players", "penalty_profiles.json")
        payload = self.repository.penalty_profiles()
        kickers = payload.get("kickers", [])
        keepers = payload.get("keepers", [])
        duel_samples = sum(int(kicker.get("sample_size", 0)) for kicker in kickers)
        return RefreshSourceStatus(
            key="penalty_intelligence",
            label="Penalty intelligence",
            status="snapshot",
            updated_at=self._payload_timestamp(payload, path),
            source="Tournament shootout profile snapshot",
            detail=f"{len(kickers)} kickers and {len(keepers)} keepers are profiled across {duel_samples} sampled penalty attempts.",
        )

    def status(self) -> RefreshStatusResponse:
        sources = [
            self._tournament_source(),
            self._fixture_sync_source(),
            self._xg_source(),
            self._penalty_source(),
        ]
        statuses = {source.status for source in sources}
        if "attention" in statuses:
            overall_status = "attention"
        elif "live" in statuses:
            overall_status = "live"
        else:
            overall_status = "snapshot"

        return RefreshStatusResponse(
            overall_status=overall_status,
            generated_at=datetime.now(tz=timezone.utc).isoformat(timespec="minutes").replace("+00:00", "Z"),
            sources=sources,
        )
