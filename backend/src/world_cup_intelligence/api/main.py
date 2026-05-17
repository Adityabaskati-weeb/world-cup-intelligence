from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from world_cup_intelligence.config import get_tournament_config
from world_cup_intelligence.data.repository import SnapshotRepository
from world_cup_intelligence.schemas.api import (
    MatchPredictionRequest,
    MatchPredictionResponse,
    PenaltyPredictionRequest,
    PenaltyPredictionResponse,
    TeamStanding,
    TournamentCurrentResponse,
    TournamentSimulationRequest,
    TournamentSimulationResponse,
    XgProfileResponse,
)
from world_cup_intelligence.services.penalty import PenaltyService
from world_cup_intelligence.services.predictor import MatchPredictorService
from world_cup_intelligence.services.simulation import SimulationService
from world_cup_intelligence.services.tournament import TournamentService
from world_cup_intelligence.services.xg import XgService

app = FastAPI(title="World Cup Intelligence 2026", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

repository = SnapshotRepository()
tournament_service = TournamentService(repository)
predictor_service = MatchPredictorService(repository)
xg_service = XgService(repository)
penalty_service = PenaltyService(repository)
simulation_service = SimulationService(repository)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/tournament/current", response_model=TournamentCurrentResponse)
def get_current_tournament() -> TournamentCurrentResponse:
    config = get_tournament_config()
    return TournamentCurrentResponse(
        slug=config.slug,
        name=config.name,
        start_date=config.start_date,
        end_date=config.end_date,
        host_countries=config.host_countries,
        host_cities=config.host_cities,
        format=config.format,
        groups=tournament_service.groups(),
    )


@app.get("/api/fixtures")
def get_fixtures(stage: str | None = None) -> dict[str, list[dict[str, str]]]:
    fixtures = tournament_service.fixtures()
    if stage:
        fixtures = [fixture for fixture in fixtures if fixture["stage"] == stage]
    return {"fixtures": fixtures}


@app.get("/api/standings", response_model=list[TeamStanding])
def get_standings() -> list[TeamStanding]:
    return [TeamStanding(**standing) for standing in tournament_service.standings()]


@app.get("/api/groups")
def get_groups() -> dict[str, dict[str, list[str]]]:
    return {"groups": tournament_service.groups()}


@app.get("/api/teams")
def get_teams() -> dict[str, list[dict[str, str]]]:
    return {"teams": repository.teams()}


@app.get("/api/players")
def get_players() -> dict[str, list[dict[str, str]]]:
    keepers = repository.penalty_profiles()["keepers"]
    kickers = repository.penalty_profiles()["kickers"]
    return {"players": repository.players(), "kickers": kickers, "keepers": keepers}


@app.post("/api/predict/match", response_model=MatchPredictionResponse)
def predict_match(request: MatchPredictionRequest) -> MatchPredictionResponse:
    try:
        return predictor_service.predict(request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown team in request: {exc}") from exc


@app.get("/api/xg/team/{team_id}", response_model=XgProfileResponse)
def get_team_xg(team_id: str) -> XgProfileResponse:
    try:
        return xg_service.team_profile(team_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown team_id: {team_id}") from exc


@app.get("/api/xg/player/{player_id}", response_model=XgProfileResponse)
def get_player_xg(player_id: str) -> XgProfileResponse:
    try:
        return xg_service.player_profile(player_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown player_id: {player_id}") from exc


@app.post("/api/predict/penalty", response_model=PenaltyPredictionResponse)
def predict_penalty(request: PenaltyPredictionRequest) -> PenaltyPredictionResponse:
    try:
        return penalty_service.predict(request)
    except StopIteration as exc:
        raise HTTPException(status_code=404, detail="Unknown penalty profile requested.") from exc


@app.post("/api/simulate/tournament", response_model=TournamentSimulationResponse)
def simulate_tournament(request: TournamentSimulationRequest) -> TournamentSimulationResponse:
    return simulation_service.simulate(request)
