from __future__ import annotations

import json
from pathlib import Path

from statsbombpy import sb

from world_cup_intelligence.data.adapters import statsbomb_world_cup_competitions

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET = REPO_ROOT / "data" / "snapshots" / "statsbomb_open_data.json"


def fetch_statsbomb_open_data() -> None:
    snapshot: dict[str, list[dict[str, object]]] = {"competitions": [], "matches": []}
    try:
        for competition_id, season_id in statsbomb_world_cup_competitions():
            matches = sb.matches(competition_id=competition_id, season_id=season_id)
            snapshot["competitions"].append({"competition_id": competition_id, "season_id": season_id})
            snapshot["matches"].extend(matches.head(10).to_dict(orient="records"))
    except Exception:
        if TARGET.exists():
            print(f"Skipping StatsBomb fetch: upstream request failed. Keeping existing snapshot at {TARGET}")
            return
        raise

    TARGET.write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")
    print(f"Wrote StatsBomb snapshot to {TARGET}")


if __name__ == "__main__":
    fetch_statsbomb_open_data()
