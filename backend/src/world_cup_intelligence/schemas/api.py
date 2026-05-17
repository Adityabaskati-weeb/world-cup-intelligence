from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ApiModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


class HealthResponse(ApiModel):
    status: str
    runtime_mode: str
    active_tournament: str


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


class FixturesResponse(ApiModel):
    fixtures: list[Fixture]


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


class GroupsResponse(ApiModel):
    groups: dict[str, list[str]]


class TeamProfileResponse(ApiModel):
    team_id: str
    name: str
    group: str
    confederation: str
    host: bool


class TeamsResponse(ApiModel):
    teams: list[TeamProfileResponse]


class PlayerProfileResponse(ApiModel):
    player_id: str
    player_name: str
    team: str


class KickerProfileResponse(ApiModel):
    player_id: str
    player_name: str
    team: str | None = None
    preferred_foot: str | None = None


class KeeperProfileResponse(ApiModel):
    keeper_id: str
    keeper_name: str
    team: str | None = None


class PlayersResponse(ApiModel):
    players: list[PlayerProfileResponse]
    kickers: list[KickerProfileResponse]
    keepers: list[KeeperProfileResponse]


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

    @model_validator(mode="after")
    def validate_distinct_teams(self) -> "MatchPredictionRequest":
        if self.home_team == self.away_team:
            raise ValueError("home_team and away_team must be different.")
        return self


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
    factors: list["PredictionFactor"] = Field(default_factory=list)
    momentum: "MomentumRead"
    narrative: list[str] = Field(default_factory=list)


class PredictionFactor(ApiModel):
    key: str
    label: str
    edge_team: str
    edge_value: float
    impact_score: float
    summary: str


class MomentumRead(ApiModel):
    edge_team: str
    swing_index: float
    confidence_band: str
    volatility: str
    summary: str


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


class XgCatalogTeam(ApiModel):
    team_id: str
    label: str


class XgCatalogPlayer(ApiModel):
    player_id: str
    player_name: str
    team: str


class XgCatalogResponse(ApiModel):
    teams: list[XgCatalogTeam]
    players: list[XgCatalogPlayer]


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


class RuntimeOverview(ApiModel):
    mode: str
    use_demo_data: bool
    active_tournament: str
    runtime_root: str
    tracking_backend: str


class ModelOverview(ApiModel):
    slug: str
    version: str
    training_window: str
    sample_size: int
    selected_model_kind: str | None = None
    test_accuracy: float | None = None
    test_macro_f1: float | None = None
    validation_macro_f1: float | None = None
    generalization_gap: float | None = None


class WorkflowOverview(ApiModel):
    workflow_name: str
    status: str
    finished_at: str | None = None
    step_count: int


class EndpointMetric(ApiModel):
    path: str
    count: int
    error_count: int
    avg_duration_ms: float


class RequestMetrics(ApiModel):
    total_requests: int
    error_requests: int
    uptime_seconds: float
    top_paths: list[EndpointMetric]


class SystemOverviewResponse(ApiModel):
    runtime: RuntimeOverview
    models: list[ModelOverview]
    workflows: list[WorkflowOverview]
    request_metrics: RequestMetrics


class RefreshSourceStatus(ApiModel):
    key: str
    label: str
    status: str
    updated_at: str | None = None
    source: str | None = None
    detail: str


class RefreshStatusResponse(ApiModel):
    overall_status: str
    generated_at: str
    sources: list[RefreshSourceStatus]
