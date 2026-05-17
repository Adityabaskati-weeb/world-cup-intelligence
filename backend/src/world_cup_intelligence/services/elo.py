from __future__ import annotations

from dataclasses import dataclass
from math import pow
from typing import Iterable


@dataclass
class EloMatch:
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    neutral: bool = True
    importance: float = 1.0


def expected_score(home_rating: float, away_rating: float, home_advantage: float = 0.0) -> float:
    return 1.0 / (1.0 + pow(10.0, ((away_rating - (home_rating + home_advantage)) / 400.0)))


def update_elo(
    ratings: dict[str, float],
    match: EloMatch,
    k_factor: float = 24.0,
    home_advantage: float = 75.0,
) -> dict[str, float]:
    home = ratings.get(match.home_team, 1500.0)
    away = ratings.get(match.away_team, 1500.0)
    advantage = 0.0 if match.neutral else home_advantage
    expected_home = expected_score(home, away, advantage)

    if match.home_goals > match.away_goals:
        actual_home = 1.0
    elif match.home_goals < match.away_goals:
        actual_home = 0.0
    else:
        actual_home = 0.5

    margin = max(1.0, abs(match.home_goals - match.away_goals))
    swing = k_factor * match.importance * (1.0 + (margin - 1.0) * 0.15)
    delta = swing * (actual_home - expected_home)

    ratings[match.home_team] = home + delta
    ratings[match.away_team] = away - delta
    return ratings


def build_ratings(matches: Iterable[EloMatch]) -> dict[str, float]:
    ratings: dict[str, float] = {}
    for match in matches:
        update_elo(ratings, match)
    return ratings

