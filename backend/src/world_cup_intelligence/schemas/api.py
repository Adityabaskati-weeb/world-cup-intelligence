from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


class Fixture(ApiModel):
    match_id: str
    stage: str
    date: str
    kickoff_local: str
    venue: str
    group: str | None = None
    home_team: str
    away_team: str
    status: str = "scheduled"


class TeamStanding(ApiModel):
    group: str
    team: str
    points: int
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    rank: int


class TournamentCurrentResponse(ApiModel):
    slug: str
    name: str
    start_date: str
    end_date: str
    host_countries: list[str]
    host_cities: list[str]
    format: dict[str, Any]
    groups: dict[str, list[str]]


class MatchPredictionRequest(ApiModel):
    home_team: str
    away_team: str
    match_date: str | None = None
    neutral_site: bool = True
    stage: str = "group"


class MatchPredictionResponse(ApiModel):
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    projected_winner: str
    model_version: str
    training_window: str
    sample_size: int
    mode: str
    top_drivers: list[str]


class XgPoint(ApiModel):
    player_id: str
    player_name: str
    minute: int
    x: float
    y: float
    xg: float
    outcome: str
    body_part: str
    situation: str


class XgProfileResponse(ApiModel):
    scope: str
    target_id: str
    label: str
    team: str
    total_xg: float
    actual_goals: int
    finishing_delta: float
    shots: list[XgPoint]
    zones: list[dict[str, Any]]
    model_version: str
    training_window: str
    sample_size: int


class PenaltyPredictionRequest(ApiModel):
    player_id: str
    keeper_id: str
    context: dict[str, Any] = Field(default_factory=dict)


class PenaltyPredictionResponse(ApiModel):
    player_id: str
    keeper_id: str
    scoring_probability: float
    likely_target_zone: str
    target_zone_probabilities: dict[str, float]
    model_version: str
    training_window: str
    sample_size: int
    notes: list[str]


class BracketMatch(ApiModel):
    match_id: str
    stage: str
    venue: str
    slot_home: str
    slot_away: str
    home_team: str | None = None
    away_team: str | None = None
    winner: str | None = None
    resolution: str | None = None


class TournamentSimulationRequest(ApiModel):
    seed: int = 2026
    assumptions: dict[str, Any] = Field(default_factory=dict)


class TournamentSimulationResponse(ApiModel):
    qualified_third_place: list[str]
    round_of_32: list[BracketMatch]
    round_of_16: list[BracketMatch]
    quarterfinals: list[BracketMatch]
    semifinals: list[BracketMatch]
    final: BracketMatch
    champion: str
