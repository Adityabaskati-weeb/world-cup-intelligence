from __future__ import annotations

import json
import os
from pathlib import Path

import requests

from world_cup_intelligence.data.adapters import FOOTBALL_DATA_MATCHES_URL, football_data_headers

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET = REPO_ROOT / "data" / "snapshots" / "football_data_snapshot.json"


def _write_placeholder_snapshot(reason: str) -> None:
    payload = {
        "source": "football-data.org",
        "status": "unavailable",
        "reason": reason,
        "matches": [],
    }
    TARGET.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote placeholder football-data.org snapshot to {TARGET}")


def fetch_football_data_snapshot() -> None:
    token = os.getenv("FOOTBALL_DATA_API_TOKEN")
    if not token:
        if TARGET.exists():
            print(f"Skipping football-data.org fetch: FOOTBALL_DATA_API_TOKEN is not configured. Keeping existing snapshot at {TARGET}")
            return
        _write_placeholder_snapshot("FOOTBALL_DATA_API_TOKEN is not configured.")
        return

    try:
        response = requests.get(FOOTBALL_DATA_MATCHES_URL, headers=football_data_headers(token), timeout=30)
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else None
        if status_code in {401, 403} and TARGET.exists():
            print(f"Skipping football-data.org fetch: received {status_code} from football-data.org. Keeping existing snapshot at {TARGET}")
            return
        if status_code in {401, 403}:
            _write_placeholder_snapshot(f"football-data.org returned HTTP {status_code}.")
            return
        raise
    except requests.RequestException:
        if TARGET.exists():
            print(f"Skipping football-data.org fetch: network request failed. Keeping existing snapshot at {TARGET}")
            return
        _write_placeholder_snapshot("Network request to football-data.org failed.")
        return

    TARGET.write_text(json.dumps(response.json(), indent=2), encoding="utf-8")
    print(f"Wrote football-data.org snapshot to {TARGET}")


if __name__ == "__main__":
    fetch_football_data_snapshot()
