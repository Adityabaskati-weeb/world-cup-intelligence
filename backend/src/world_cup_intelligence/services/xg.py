from __future__ import annotations

from typing import Any

from world_cup_intelligence.data.repository import SnapshotRepository
from world_cup_intelligence.schemas.api import XgPoint, XgProfileResponse


class XgService:
    def __init__(self, repository: SnapshotRepository) -> None:
        self.repository = repository
        self.snapshot = repository.xg_profiles()

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
                    model_version="snapshot-xg-view-v1",
                    training_window="statsbomb_open_data_plus_world_cup",
                    sample_size=team["sample_size"],
                )
        raise KeyError(team_id)

    def player_profile(self, player_id: str) -> XgProfileResponse:
        for player in self.snapshot["players"]:
            if player["player_id"] == player_id:
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
                    model_version="snapshot-xg-view-v1",
                    training_window="statsbomb_open_data_plus_world_cup",
                    sample_size=player["sample_size"],
                )
        raise KeyError(player_id)

