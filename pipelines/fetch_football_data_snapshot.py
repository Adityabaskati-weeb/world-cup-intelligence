from __future__ import annotations

import json
from pathlib import Path

import requests

from world_cup_intelligence.data.adapters import FOOTBALL_DATA_MATCHES_URL, football_data_headers

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET = REPO_ROOT / "data" / "snapshots" / "football_data_snapshot.json"


def fetch_football_data_snapshot() -> None:
    response = requests.get(FOOTBALL_DATA_MATCHES_URL, headers=football_data_headers(), timeout=30)
    response.raise_for_status()
    TARGET.write_text(json.dumps(response.json(), indent=2), encoding="utf-8")
    print(f"Wrote football-data.org snapshot to {TARGET}")


if __name__ == "__main__":
    fetch_football_data_snapshot()

