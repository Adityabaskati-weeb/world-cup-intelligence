from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any

from world_cup_intelligence.data.repository import SnapshotRepository


ROUND_OF_32_TEMPLATE = [
    {"match_id": "73", "stage": "round_of_32", "home_slot": "2A", "away_slot": "2B", "venue": "Los Angeles Stadium"},
    {"match_id": "74", "stage": "round_of_32", "home_slot": "1E", "away_slot": "3ABCDF", "venue": "Boston Stadium"},
    {"match_id": "75", "stage": "round_of_32", "home_slot": "1F", "away_slot": "2C", "venue": "Estadio Monterrey"},
    {"match_id": "76", "stage": "round_of_32", "home_slot": "1C", "away_slot": "2F", "venue": "Houston Stadium"},
    {"match_id": "77", "stage": "round_of_32", "home_slot": "1I", "away_slot": "3CDFGH", "venue": "New York New Jersey Stadium"},
    {"match_id": "78", "stage": "round_of_32", "home_slot": "2E", "away_slot": "2I", "venue": "Dallas Stadium"},
    {"match_id": "79", "stage": "round_of_32", "home_slot": "1A", "away_slot": "3CEFHI", "venue": "Mexico City Stadium"},
    {"match_id": "80", "stage": "round_of_32", "home_slot": "1L", "away_slot": "3EHIJK", "venue": "Atlanta Stadium"},
    {"match_id": "81", "stage": "round_of_32", "home_slot": "1D", "away_slot": "3BEFIJ", "venue": "San Francisco Bay Area Stadium"},
    {"match_id": "82", "stage": "round_of_32", "home_slot": "1G", "away_slot": "3AEHIJ", "venue": "Seattle Stadium"},
    {"match_id": "83", "stage": "round_of_32", "home_slot": "2K", "away_slot": "2L", "venue": "Toronto Stadium"},
    {"match_id": "84", "stage": "round_of_32", "home_slot": "1H", "away_slot": "2J", "venue": "Los Angeles Stadium"},
    {"match_id": "85", "stage": "round_of_32", "home_slot": "1B", "away_slot": "3EFGIJ", "venue": "BC Place Vancouver"},
    {"match_id": "86", "stage": "round_of_32", "home_slot": "1J", "away_slot": "2H", "venue": "Miami Stadium"},
    {"match_id": "87", "stage": "round_of_32", "home_slot": "1K", "away_slot": "3DEIJL", "venue": "Kansas City Stadium"},
    {"match_id": "88", "stage": "round_of_32", "home_slot": "2D", "away_slot": "2G", "venue": "Dallas Stadium"},
]

NEXT_ROUNDS = {
    "round_of_16": [
        {"match_id": "89", "venue": "Philadelphia Stadium", "home_slot": "W74", "away_slot": "W77"},
        {"match_id": "90", "venue": "Houston Stadium", "home_slot": "W73", "away_slot": "W75"},
        {"match_id": "91", "venue": "New York New Jersey Stadium", "home_slot": "W76", "away_slot": "W78"},
        {"match_id": "92", "venue": "Mexico City Stadium", "home_slot": "W79", "away_slot": "W80"},
        {"match_id": "93", "venue": "Dallas Stadium", "home_slot": "W83", "away_slot": "W84"},
        {"match_id": "94", "venue": "Seattle Stadium", "home_slot": "W81", "away_slot": "W82"},
        {"match_id": "95", "venue": "Atlanta Stadium", "home_slot": "W86", "away_slot": "W88"},
        {"match_id": "96", "venue": "BC Place Vancouver", "home_slot": "W85", "away_slot": "W87"},
    ],
    "quarterfinal": [
        {"match_id": "97", "venue": "Boston Stadium", "home_slot": "W89", "away_slot": "W90"},
        {"match_id": "98", "venue": "Los Angeles Stadium", "home_slot": "W93", "away_slot": "W94"},
        {"match_id": "99", "venue": "Miami Stadium", "home_slot": "W91", "away_slot": "W92"},
        {"match_id": "100", "venue": "Kansas City Stadium", "home_slot": "W95", "away_slot": "W96"},
    ],
    "semifinal": [
        {"match_id": "101", "venue": "Dallas Stadium", "home_slot": "W97", "away_slot": "W98"},
        {"match_id": "102", "venue": "Atlanta Stadium", "home_slot": "W99", "away_slot": "W100"},
    ],
    "final": [
        {"match_id": "104", "venue": "MetLife Stadium", "home_slot": "W101", "away_slot": "W102"},
    ],
}


@dataclass
class QualifiedTeam:
    slot: str
    team: str
    group: str
    points: int
    goal_difference: int
    goals_for: int


class TournamentService:
    def __init__(self, repository: SnapshotRepository) -> None:
        self.repository = repository

    def standings(self) -> list[dict[str, Any]]:
        return self.repository.standings()

    def groups(self) -> dict[str, list[str]]:
        return self.repository.groups()

    def fixtures(self) -> list[dict[str, Any]]:
        return self.repository.fixtures()

    def _group_rows(self, group: str) -> list[dict[str, Any]]:
        rows = [row for row in self.repository.standings() if row["group"] == group]
        return sorted(rows, key=lambda row: (-row["points"], -row["goal_difference"], -row["goals_for"], row["team"]))

    def top_two(self) -> list[QualifiedTeam]:
        qualified: list[QualifiedTeam] = []
        for group in sorted(self.groups()):
            rows = self._group_rows(group)
            for index, row in enumerate(rows[:2], start=1):
                qualified.append(
                    QualifiedTeam(
                        slot=f"{index}{group}",
                        team=row["team"],
                        group=group,
                        points=row["points"],
                        goal_difference=row["goal_difference"],
                        goals_for=row["goals_for"],
                    )
                )
        return qualified

    def best_third_place(self) -> list[QualifiedTeam]:
        thirds: list[QualifiedTeam] = []
        for group in sorted(self.groups()):
            row = self._group_rows(group)[2]
            thirds.append(
                QualifiedTeam(
                    slot=f"3{group}",
                    team=row["team"],
                    group=group,
                    points=row["points"],
                    goal_difference=row["goal_difference"],
                    goals_for=row["goals_for"],
                )
            )
        thirds.sort(key=lambda row: (-row.points, -row.goal_difference, -row.goals_for, row.team))
        return thirds[:8]

    def resolve_third_place_slots(self, teams: list[QualifiedTeam]) -> dict[str, QualifiedTeam]:
        slots = [template for template in ROUND_OF_32_TEMPLATE if template["away_slot"].startswith("3")]
        by_group = {team.group: team for team in teams}
        slot_groups = {template["match_id"]: list(template["away_slot"][1:]) for template in slots}

        ordered_slots = sorted(slots, key=lambda template: len(slot_groups[template["match_id"]]))
        assignment: dict[str, QualifiedTeam] = {}
        used_groups: set[str] = set()

        def backtrack(index: int) -> bool:
            if index == len(ordered_slots):
                return True
            template = ordered_slots[index]
            match_id = template["match_id"]
            eligible_groups = [group for group in slot_groups[match_id] if group in by_group and group not in used_groups]
            eligible_groups.sort(key=lambda group: next(position for position, team in enumerate(teams) if team.group == group))
            for group in eligible_groups:
                assignment[match_id] = by_group[group]
                used_groups.add(group)
                if backtrack(index + 1):
                    return True
                used_groups.remove(group)
                assignment.pop(match_id, None)
            return False

        if not backtrack(0):
            raise ValueError("Could not allocate third-place teams to round-of-32 slots.")
        return assignment

