from __future__ import annotations

import pandas as pd

from world_cup_intelligence.data.repository import SnapshotRepository
from world_cup_intelligence.schemas.api import PenaltyPredictionRequest, PenaltyPredictionResponse
from world_cup_intelligence.services.errors import ModelArtifactUnavailableError
from world_cup_intelligence.services.training import load_artifact


class PenaltyService:
    def __init__(self, repository: SnapshotRepository) -> None:
        self.repository = repository
        self.snapshot = repository.penalty_profiles()

    @property
    def artifact(self) -> dict[str, object] | None:
        return load_artifact("penalty_model.joblib")

    @staticmethod
    def _match_state(context: dict[str, object]) -> int:
        if "match_state" in context:
            return int(context["match_state"])
        stage = str(context.get("tournament_stage", "group")).lower()
        if stage in {"round_of_32", "round_of_16", "quarterfinal", "semifinal", "final", "knockout"}:
            return 1
        return 0

    def _feature_row(self, kicker: dict[str, object], keeper: dict[str, object], request: PenaltyPredictionRequest) -> dict[str, float]:
        pressure = float(request.context.get("pressure", 0.5))
        preferred_zone = str(kicker["preferred_zone"])
        keeper_bias = float(keeper["save_bias"].get(preferred_zone, 0.2))
        return {
            "pressure": pressure,
            "footedness_code": float(kicker.get("footedness_code", 1)),
            "keeper_bias": keeper_bias,
            "match_state": float(self._match_state(request.context)),
        }

    def predict(self, request: PenaltyPredictionRequest) -> PenaltyPredictionResponse:
        kicker = next(player for player in self.snapshot["kickers"] if player["player_id"] == request.player_id)
        keeper = next(player for player in self.snapshot["keepers"] if player["keeper_id"] == request.keeper_id)
        features = self._feature_row(kicker, keeper, request)
        artifact = self.artifact
        if artifact is None:
            raise ModelArtifactUnavailableError("penalty")

        feature_columns = list(artifact["features"])
        frame = pd.DataFrame([features], columns=feature_columns)
        placement_model = artifact["placement_model"]
        conversion_model = artifact["conversion_model"]

        placement_probabilities = placement_model.predict_proba(frame)[0]
        placement_classes = artifact.get("placement_classes") or list(placement_model.classes_)
        target_zone_probabilities = {
            str(label): round(float(probability), 4)
            for label, probability in zip(placement_classes, placement_probabilities, strict=True)
        }
        likely_target_zone = max(target_zone_probabilities, key=target_zone_probabilities.get)

        conversion_classes = list(conversion_model.classes_)
        positive_index = conversion_classes.index(1) if 1 in conversion_classes else -1
        scoring_probability = round(float(conversion_model.predict_proba(frame)[0][positive_index]), 4)

        notes = [
            f"{kicker['player_name']} profile: {kicker.get('preferred_foot', 'preferred-foot unknown')} foot, usual target {kicker['preferred_zone']}.",
            f"{keeper['keeper_name']} suppresses {kicker['preferred_zone']} with bias {features['keeper_bias']:.2f}.",
            f"Model pressure input: {features['pressure']:.2f}; state input: {int(features['match_state'])}.",
        ]
        return PenaltyPredictionResponse(
            player_id=request.player_id,
            keeper_id=request.keeper_id,
            scoring_probability=scoring_probability,
            likely_target_zone=likely_target_zone,
            target_zone_probabilities=target_zone_probabilities,
            model_version=artifact["version"],
            training_window=artifact["training_window"],
            sample_size=int(artifact["sample_size"]),
            notes=notes,
        )
