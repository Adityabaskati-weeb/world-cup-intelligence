from __future__ import annotations

import json
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET = REPO_ROOT / "data" / "snapshots" / "tournaments" / "world_cup_2026_live.json"
OPENFOOTBALL_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"


def fetch_tournament_snapshot() -> None:
    try:
        response = requests.get(OPENFOOTBALL_URL, timeout=30)
        response.raise_for_status()
    except requests.RequestException:
        if TARGET.exists():
            print(f"Skipping tournament snapshot fetch: network request failed. Keeping existing snapshot at {TARGET}")
            return
        raise

    payload = response.json()
    TARGET.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote tournament snapshot to {TARGET}")


if __name__ == "__main__":
    fetch_tournament_snapshot()
