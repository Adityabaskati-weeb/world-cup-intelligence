from __future__ import annotations

from world_cup_intelligence.data.repository import SnapshotRepository
from world_cup_intelligence.schemas.api import PenaltyPredictionRequest, PenaltyPredictionResponse


class PenaltyService:
    def __init__(self, repository: SnapshotRepository) -> None:
        self.repository = repository
        self.snapshot = repository.penalty_profiles()

    def predict(self, request: PenaltyPredictionRequest) -> PenaltyPredictionResponse:
        kicker = next(player for player in self.snapshot["kickers"] if player["player_id"] == request.player_id)
        keeper = next(player for player in self.snapshot["keepers"] if player["keeper_id"] == request.keeper_id)

        pressure = float(request.context.get("pressure", 0.5))
        keeper_bias = keeper["save_bias"].get(kicker["preferred_zone"], 0.2)
        base = kicker["conversion_rate"] - (keeper["save_rate"] * 0.35) - (pressure * 0.08) - (keeper_bias * 0.05)
        scoring_probability = min(0.95, max(0.45, base))
        return PenaltyPredictionResponse(
            player_id=request.player_id,
            keeper_id=request.keeper_id,
            scoring_probability=round(scoring_probability, 4),
            likely_target_zone=kicker["preferred_zone"],
            target_zone_probabilities=kicker["target_zone_probabilities"],
            model_version="penalty-profile-v1",
            training_window="major_tournaments_open_data",
            sample_size=int(kicker["sample_size"]),
            notes=[
                f"{kicker['player_name']} prefers {kicker['preferred_zone']}.",
                f"{keeper['keeper_name']} save rate: {keeper['save_rate']:.2f}.",
                "Pressure adjustment applied from request context.",
            ],
        )

