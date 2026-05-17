from fastapi.testclient import TestClient

import world_cup_intelligence.services.penalty as penalty_module
import world_cup_intelligence.services.predictor as predictor_module
from world_cup_intelligence.api.main import app


client = TestClient(app)


def test_tournament_current_endpoint() -> None:
    response = client.get("/api/tournament/current")
    assert response.status_code == 200
    payload = response.json()
    assert payload["slug"] == "world_cup_2026"
    assert payload["format"]["group_count"] == 12


def test_health_endpoint_exposes_runtime_mode() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["runtime_mode"] in {"snapshot_backed_api", "live_api"}


def test_fixtures_endpoint_allows_knockout_null_groups() -> None:
    response = client.get("/api/fixtures")
    assert response.status_code == 200
    payload = response.json()
    assert payload["fixtures"]
    assert any(fixture["group"] is None for fixture in payload["fixtures"])


def test_groups_endpoint() -> None:
    response = client.get("/api/groups")
    assert response.status_code == 200
    payload = response.json()
    assert "groups" in payload
    assert len(payload["groups"]) == 12


def test_xg_catalog_endpoint() -> None:
    response = client.get("/api/xg/catalog")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["teams"]) >= 6
    assert any(player["player_id"] == "rodrygo" for player in payload["players"])


def test_xg_player_endpoint_supports_derived_shot_profiles() -> None:
    response = client.get("/api/xg/player/rodrygo")
    assert response.status_code == 200
    payload = response.json()
    assert payload["label"] == "Rodrygo"
    assert payload["shots"]


def test_system_overview_endpoint() -> None:
    client.get("/api/tournament/current")
    client.get("/api/fixtures")
    response = client.get("/api/system/overview")
    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime"]["active_tournament"] == "world_cup_2026"
    assert payload["runtime"]["mode"] in {"snapshot_backed_api", "live_api"}
    assert any(model["slug"] == "match" for model in payload["models"])
    assert payload["request_metrics"]["total_requests"] >= 3


def test_refresh_status_endpoint() -> None:
    response = client.get("/api/refresh/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["overall_status"] in {"live", "snapshot", "attention"}
    assert any(source["key"] == "fixture_sync" for source in payload["sources"])


def test_match_predictor_endpoint() -> None:
    response = client.post(
        "/api/predict/match",
        json={"home_team": "Mexico", "away_team": "South Africa", "neutral_site": False},
    )
    assert response.status_code == 200
    payload = response.json()
    total = payload["home_win_probability"] + payload["draw_probability"] + payload["away_win_probability"]
    assert round(total, 4) == 1.0
    assert payload["factors"]
    assert payload["momentum"]["confidence_band"]
    assert payload["narrative"]


def test_match_predictor_rejects_same_team_fixture() -> None:
    response = client.post(
        "/api/predict/match",
        json={"home_team": "Mexico", "away_team": "Mexico", "neutral_site": False},
    )
    assert response.status_code == 422
    assert "must be different" in response.text


def test_match_predictor_returns_503_when_model_artifact_is_missing(monkeypatch) -> None:
    monkeypatch.setattr(predictor_module, "load_artifact", lambda _: None)

    response = client.post(
        "/api/predict/match",
        json={"home_team": "Mexico", "away_team": "South Africa", "neutral_site": False},
    )

    assert response.status_code == 503
    assert "match model artifact is unavailable" in response.text


def test_simulation_endpoint_uses_penalties_when_needed() -> None:
    response = client.post("/api/simulate/tournament", json={"seed": 2026})
    assert response.status_code == 200
    payload = response.json()
    assert payload["champion"]
    assert payload["final"]["winner"]


def test_penalty_endpoint_returns_model_notes() -> None:
    response = client.post(
        "/api/predict/penalty",
        json={
            "player_id": "harry-kane",
            "keeper_id": "emiliano-martinez",
            "context": {"pressure": 0.85, "tournament_stage": "knockout"},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["target_zone_probabilities"]
    assert payload["notes"]


def test_penalty_endpoint_returns_503_when_model_artifact_is_missing(monkeypatch) -> None:
    monkeypatch.setattr(penalty_module, "load_artifact", lambda _: None)

    response = client.post(
        "/api/predict/penalty",
        json={
            "player_id": "harry-kane",
            "keeper_id": "emiliano-martinez",
            "context": {"pressure": 0.85, "tournament_stage": "knockout"},
        },
    )

    assert response.status_code == 503
    assert "penalty model artifact is unavailable" in response.text
