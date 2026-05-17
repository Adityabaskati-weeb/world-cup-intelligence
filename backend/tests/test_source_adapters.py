from world_cup_intelligence.data.adapters import (
    FIFA_MATCH_SCHEDULE_URL,
    FIFA_QUALIFIED_TEAMS_URL,
    FOOTBALL_DATA_MATCHES_URL,
    INTERNATIONAL_RESULTS_URL,
    OPENFOOTBALL_2026_URL,
    SHOOTOUTS_URL,
    football_data_headers,
    statsbomb_world_cup_competitions,
)


def test_source_urls_are_wired() -> None:
    assert "fifa.com" in FIFA_MATCH_SCHEDULE_URL
    assert "fifa.com" in FIFA_QUALIFIED_TEAMS_URL
    assert "api.football-data.org" in FOOTBALL_DATA_MATCHES_URL
    assert INTERNATIONAL_RESULTS_URL.endswith("results.csv")
    assert SHOOTOUTS_URL.endswith("shootouts.csv")
    assert OPENFOOTBALL_2026_URL.endswith("/2026/worldcup.json")


def test_football_data_headers_optional() -> None:
    assert football_data_headers(None) == {}
    assert football_data_headers("demo-token") == {"X-Auth-Token": "demo-token"}


def test_statsbomb_competitions_include_2018_and_2022() -> None:
    assert statsbomb_world_cup_competitions() == [(43, 3), (43, 106)]
