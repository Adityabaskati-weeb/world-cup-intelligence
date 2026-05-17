from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from world_cup_intelligence.config import snapshot_path


class SnapshotRepository:
    def __init__(self, tournament_slug: str = "world_cup_2026") -> None:
        self.tournament_slug = tournament_slug

    def _read_json(self, path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    @lru_cache(maxsize=1)
    def tournament_snapshot(self) -> dict[str, Any]:
        return self._read_json(snapshot_path("tournaments", f"{self.tournament_slug}.json"))

    @lru_cache(maxsize=1)
    def xg_profiles(self) -> dict[str, Any]:
        return self._read_json(snapshot_path("players", "xg_profiles.json"))

    @lru_cache(maxsize=1)
    def penalty_profiles(self) -> dict[str, Any]:
        return self._read_json(snapshot_path("players", "penalty_profiles.json"))

    def groups(self) -> dict[str, list[str]]:
        return self.tournament_snapshot()["groups"]

    def fixtures(self) -> list[dict[str, Any]]:
        return self.tournament_snapshot()["fixtures"]

    def standings(self) -> list[dict[str, Any]]:
        snapshot = self.tournament_snapshot()
        if "standings" in snapshot:
            return snapshot["standings"]

        rows: list[dict[str, Any]] = []
        grouped = snapshot["groups"]
        team_lookup = {team["name"]: team for team in snapshot["teams"]}
        for group, teams in grouped.items():
            ranked = sorted(
                teams,
                key=lambda team_name: (
                    -team_lookup[team_name]["projected_points"],
                    -team_lookup[team_name]["projected_goal_difference"],
                    -team_lookup[team_name]["projected_goals_for"],
                    team_name,
                ),
            )
            for rank, team_name in enumerate(ranked, start=1):
                profile = team_lookup[team_name]
                rows.append(
                    {
                        "group": group,
                        "team": team_name,
                        "points": profile["projected_points"],
                        "played": 3,
                        "won": profile["projected_won"],
                        "drawn": profile["projected_drawn"],
                        "lost": profile["projected_lost"],
                        "goals_for": profile["projected_goals_for"],
                        "goals_against": profile["projected_goals_against"],
                        "goal_difference": profile["projected_goal_difference"],
                        "rank": rank,
                    }
                )
        return rows

    def teams(self) -> list[dict[str, Any]]:
        return self.tournament_snapshot()["teams"]

    def players(self) -> list[dict[str, Any]]:
        return self.xg_profiles()["players"]

    def xg_teams(self) -> list[dict[str, Any]]:
        return self.xg_profiles()["teams"]

    def team_lookup(self) -> dict[str, dict[str, Any]]:
        return {team["name"]: team for team in self.teams()}

    def player_lookup(self) -> dict[str, dict[str, Any]]:
        return {player["player_id"]: player for player in self.players()}

    def kicker_lookup(self) -> dict[str, dict[str, Any]]:
        return {kicker["player_id"]: kicker for kicker in self.penalty_profiles()["kickers"]}

    def keeper_lookup(self) -> dict[str, dict[str, Any]]:
        return {keeper["keeper_id"]: keeper for keeper in self.penalty_profiles()["keepers"]}

    def kicker_for_team(self, team_name: str) -> dict[str, Any] | None:
        return next((kicker for kicker in self.penalty_profiles()["kickers"] if kicker.get("team") == team_name), None)

    def keeper_for_team(self, team_name: str) -> dict[str, Any] | None:
        return next((keeper for keeper in self.penalty_profiles()["keepers"] if keeper.get("team") == team_name), None)
