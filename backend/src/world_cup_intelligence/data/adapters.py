from __future__ import annotations

import os


FIFA_MATCH_SCHEDULE_URL = "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/match-schedule-fixtures-results-teams-stadiums"
FIFA_QUALIFIED_TEAMS_URL = "https://www.fifa.com/en/articles/world-cup-2026-who-has-qualified?searchOverlay=1"
OPENFOOTBALL_2026_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
INTERNATIONAL_RESULTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
SHOOTOUTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/shootouts.csv"
FOOTBALL_DATA_MATCHES_URL = "https://api.football-data.org/v4/competitions/WC/matches"


def football_data_headers(token: str | None = None) -> dict[str, str]:
    resolved = token or os.getenv("FOOTBALL_DATA_API_TOKEN")
    if not resolved:
        return {}
    return {"X-Auth-Token": resolved}


def statsbomb_world_cup_competitions() -> list[tuple[int, int]]:
    return [(43, 3), (43, 106)]
