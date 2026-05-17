from __future__ import annotations

from collections import defaultdict
from typing import Any

from world_cup_intelligence.data.repository import SnapshotRepository
from world_cup_intelligence.schemas.api import XgPoint, XgProfileResponse
from world_cup_intelligence.services.model_runtime import load_artifact


class XgService:
    def __init__(self, repository: SnapshotRepository) -> None:
        self.repository = repository
        self.snapshot = repository.xg_profiles()
        self.players_by_id = self._build_player_profiles()

    @property
    def artifact(self) -> dict[str, object] | None:
        return load_artifact("xg_model.joblib")

    @property
    def _model_version(self) -> str:
        return self.artifact["version"] if self.artifact else "snapshot-xg-view-v1"

    @property
    def _training_window(self) -> str:
        return self.artifact["training_window"] if self.artifact else "statsbomb_open_data_plus_world_cup"

    @property
    def _sample_size(self) -> int:
        return int(self.artifact["sample_size"]) if self.artifact else 0

    def team_profile(self, team_id: str) -> XgProfileResponse:
        for team in self.snapshot["teams"]:
            if team["team_id"] == team_id:
                shots = [XgPoint(**shot) for shot in team["shots"]]
                return XgProfileResponse(
                    scope="team",
                    target_id=team_id,
                    label=team["label"],
                    team=team["label"],
                    total_xg=team["total_xg"],
                    actual_goals=team["actual_goals"],
                    finishing_delta=round(team["actual_goals"] - team["total_xg"], 3),
                    shots=shots,
                    zones=team["zones"],
                    model_version=self._model_version,
                    training_window=self._training_window,
                    sample_size=int(team["sample_size"] or self._sample_size),
                )
        raise KeyError(team_id)

    def catalog(self) -> dict[str, list[dict[str, str]]]:
        return {
            "teams": [{"team_id": team["team_id"], "label": team["label"]} for team in self.snapshot["teams"]],
            "players": [
                {
                    "player_id": player["player_id"],
                    "player_name": player["player_name"],
                    "team": player["team"],
                }
                for player in sorted(
                    self.players_by_id.values(),
                    key=lambda player: (str(player["team"]), str(player["player_name"])),
                )
            ],
        }

    def player_profile(self, player_id: str) -> XgProfileResponse:
        player = self.players_by_id.get(player_id)
        if player:
            shots = [XgPoint(**shot) for shot in player["shots"]]
            return XgProfileResponse(
                scope="player",
                target_id=player_id,
                label=player["player_name"],
                team=player["team"],
                total_xg=player["total_xg"],
                actual_goals=player["actual_goals"],
                finishing_delta=round(player["actual_goals"] - player["total_xg"], 3),
                shots=shots,
                zones=player["zones"],
                model_version=self._model_version,
                training_window=self._training_window,
                sample_size=int(player["sample_size"] or self._sample_size),
            )
        raise KeyError(player_id)

    def _build_player_profiles(self) -> dict[str, dict[str, Any]]:
        explicit_profiles = {
            str(player["player_id"]): {
                "player_id": player["player_id"],
                "player_name": player["player_name"],
                "team": player["team"],
                "total_xg": float(player["total_xg"]),
                "actual_goals": int(player["actual_goals"]),
                "sample_size": int(player["sample_size"]),
                "zones": player["zones"],
                "shots": player["shots"],
            }
            for player in self.snapshot["players"]
        }

        derived_profiles: dict[str, dict[str, Any]] = {}
        for team in self.snapshot["teams"]:
            grouped_shots: dict[str, list[dict[str, Any]]] = defaultdict(list)
            player_names: dict[str, str] = {}
            player_xg: dict[str, float] = defaultdict(float)
            player_goals: dict[str, int] = defaultdict(int)

            for shot in team["shots"]:
                player_id = str(shot["player_id"])
                grouped_shots[player_id].append(shot)
                player_names[player_id] = str(shot["player_name"])
                player_xg[player_id] += float(shot["xg"])
                if str(shot["outcome"]).lower() == "goal":
                    player_goals[player_id] += 1

            grouped_zone_totals: dict[str, dict[str, dict[str, float | int]]] = defaultdict(
                lambda: defaultdict(lambda: {"shots": 0, "xg": 0.0})
            )
            for shot in team["shots"]:
                player_id = str(shot["player_id"])
                zone = self._shot_zone(float(shot["x"]), float(shot["y"]))
                grouped_zone_totals[player_id][zone]["shots"] += 1
                grouped_zone_totals[player_id][zone]["xg"] += float(shot["xg"])

            for player_id, shots in grouped_shots.items():
                derived_profiles[player_id] = {
                    "player_id": player_id,
                    "player_name": player_names[player_id],
                    "team": team["label"],
                    "total_xg": round(player_xg[player_id], 3),
                    "actual_goals": player_goals[player_id],
                    "sample_size": len(shots),
                    "zones": [
                        {
                            "zone": zone,
                            "shots": int(values["shots"]),
                            "xg": round(float(values["xg"]), 3),
                        }
                        for zone, values in sorted(
                            grouped_zone_totals[player_id].items(),
                            key=lambda item: (-float(item[1]["xg"]), item[0]),
                        )
                    ],
                    "shots": shots,
                }

        merged = explicit_profiles.copy()
        for player_id, profile in derived_profiles.items():
            merged.setdefault(player_id, profile)
        return merged

    @staticmethod
    def _shot_zone(x: float, y: float) -> str:
        if x >= 88:
            if 43 <= y <= 57:
                return "central-box"
            return "inside-box-channel"
        if x >= 80:
            if y < 43:
                return "left-inside-box"
            if y > 57:
                return "right-inside-box"
            return "box-edge"
        if x >= 72:
            if y < 43:
                return "left-half-space"
            if y > 57:
                return "right-half-space"
            return "central-pocket"
        return "long-range"
