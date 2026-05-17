from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from world_cup_intelligence.config import get_tournament_config
from world_cup_intelligence.core.logging import configure_logging, get_logger
from world_cup_intelligence.core.monitoring import request_monitor
from world_cup_intelligence.core.settings import get_settings
from world_cup_intelligence.data.repository import SnapshotRepository
from world_cup_intelligence.schemas.api import (
    FixturesResponse,
    GroupsResponse,
    HealthResponse,
    MatchPredictionRequest,
    MatchPredictionResponse,
    PenaltyPredictionRequest,
    PenaltyPredictionResponse,
    PlayersResponse,
    RefreshStatusResponse,
    SystemOverviewResponse,
    TeamStanding,
    TeamsResponse,
    TournamentCurrentResponse,
    TournamentSimulationRequest,
    TournamentSimulationResponse,
    XgCatalogResponse,
    XgProfileResponse,
)
from world_cup_intelligence.services.penalty import PenaltyService
from world_cup_intelligence.services.predictor import MatchPredictorService
from world_cup_intelligence.services.refresh import RefreshStatusService
from world_cup_intelligence.services.simulation import SimulationService
from world_cup_intelligence.services.errors import ModelArtifactUnavailableError
from world_cup_intelligence.services.system import SystemOverviewService, runtime_mode_label
from world_cup_intelligence.services.tournament import TournamentService
from world_cup_intelligence.services.xg import XgService

configure_logging()
logger = get_logger(__name__)
settings = get_settings()

app = FastAPI(title="Matchflow API", version="0.1.0")
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
system_overview_service = SystemOverviewService()
refresh_status_service = RefreshStatusService(repository)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next) -> Response:
    request_id = request.headers.get("x-request-id", str(uuid4()))
    started_at = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((perf_counter() - started_at) * 1000, 3)
        request_monitor.record(request.url.path, 500, duration_ms)
        logger.exception("Unhandled request failure request_id=%s path=%s duration_ms=%.3f", request_id, request.url.path, duration_ms)
        raise

    duration_ms = round((perf_counter() - started_at) * 1000, 3)
    request_monitor.record(request.url.path, response.status_code, duration_ms)
    response.headers["x-request-id"] = request_id
    logger.info(
        "request_id=%s method=%s path=%s status=%s duration_ms=%.3f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        runtime_mode=runtime_mode_label(settings.use_demo_data),
        active_tournament=settings.active_tournament_slug,
    )


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


@app.get("/api/fixtures", response_model=FixturesResponse)
def get_fixtures(stage: str | None = None) -> FixturesResponse:
    fixtures = tournament_service.fixtures()
    if stage:
        fixtures = [fixture for fixture in fixtures if fixture["stage"] == stage]
    return FixturesResponse(fixtures=fixtures)


@app.get("/api/standings", response_model=list[TeamStanding])
def get_standings() -> list[TeamStanding]:
    return [TeamStanding(**standing) for standing in tournament_service.standings()]


@app.get("/api/groups", response_model=GroupsResponse)
def get_groups() -> GroupsResponse:
    return GroupsResponse(groups=tournament_service.groups())


@app.get("/api/teams", response_model=TeamsResponse)
def get_teams() -> TeamsResponse:
    return TeamsResponse(teams=repository.teams())


@app.get("/api/players", response_model=PlayersResponse)
def get_players() -> PlayersResponse:
    keepers = repository.penalty_profiles()["keepers"]
    kickers = repository.penalty_profiles()["kickers"]
    return PlayersResponse(players=xg_service.catalog()["players"], kickers=kickers, keepers=keepers)


@app.get("/api/system/overview", response_model=SystemOverviewResponse)
def get_system_overview() -> SystemOverviewResponse:
    return system_overview_service.overview()


@app.get("/api/refresh/status", response_model=RefreshStatusResponse)
def get_refresh_status() -> RefreshStatusResponse:
    return refresh_status_service.status()


@app.post("/api/predict/match", response_model=MatchPredictionResponse)
def predict_match(request: MatchPredictionRequest) -> MatchPredictionResponse:
    try:
        return predictor_service.predict(request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown team in request: {exc}") from exc
    except ModelArtifactUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/xg/team/{team_id}", response_model=XgProfileResponse)
def get_team_xg(team_id: str) -> XgProfileResponse:
    try:
        return xg_service.team_profile(team_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown team_id: {team_id}") from exc


@app.get("/api/xg/catalog", response_model=XgCatalogResponse)
def get_xg_catalog() -> XgCatalogResponse:
    return XgCatalogResponse(**xg_service.catalog())


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
    except ModelArtifactUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/simulate/tournament", response_model=TournamentSimulationResponse)
def simulate_tournament(request: TournamentSimulationRequest) -> TournamentSimulationResponse:
    try:
        return simulation_service.simulate(request)
    except ModelArtifactUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
