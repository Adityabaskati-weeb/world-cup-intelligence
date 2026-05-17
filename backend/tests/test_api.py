from fastapi.testclient import TestClient

from world_cup_intelligence.api.main import app


client = TestClient(app)


def test_tournament_current_endpoint() -> None:
    response = client.get("/api/tournament/current")
    assert response.status_code == 200
    payload = response.json()
    assert payload["slug"] == "world_cup_2026"
    assert payload["format"]["group_count"] == 12


def test_match_predictor_endpoint() -> None:
    response = client.post(
        "/api/predict/match",
        json={"home_team": "Mexico", "away_team": "South Africa", "neutral_site": False},
    )
    assert response.status_code == 200
    payload = response.json()
    total = payload["home_win_probability"] + payload["draw_probability"] + payload["away_win_probability"]
    assert round(total, 4) == 1.0


def test_simulation_endpoint_uses_penalties_when_needed() -> None:
    response = client.post("/api/simulate/tournament", json={"seed": 2026})
    assert response.status_code == 200
    payload = response.json()
    assert payload["champion"]
    assert payload["final"]["winner"]
