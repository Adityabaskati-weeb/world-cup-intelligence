from __future__ import annotations

from fetch_international_results import fetch_international_results
from fetch_statsbomb_open_data import fetch_statsbomb_open_data
from fetch_football_data_snapshot import fetch_football_data_snapshot
from fetch_tournament_snapshot import fetch_tournament_snapshot
from world_cup_intelligence.orchestration.workflows import PipelineOrchestrator


def main() -> None:
    orchestrator = PipelineOrchestrator()
    orchestrator.execute(
        workflow_name="refresh_all",
        steps=[
            ("tournament_snapshot", fetch_tournament_snapshot),
            ("international_results", fetch_international_results),
            ("statsbomb_open_data", fetch_statsbomb_open_data),
            ("football_data_snapshot", fetch_football_data_snapshot),
        ],
    )


if __name__ == "__main__":
    main()
