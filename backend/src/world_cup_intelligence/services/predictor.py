from __future__ import annotations

from typing import Any

import numpy as np

from world_cup_intelligence.data.repository import SnapshotRepository
from world_cup_intelligence.schemas.api import MatchPredictionRequest, MatchPredictionResponse, MomentumRead, PredictionFactor
from world_cup_intelligence.services.errors import ModelArtifactUnavailableError
from world_cup_intelligence.services.model_runtime import MATCH_FEATURES, load_artifact


FEATURE_LABELS = {
    "elo_diff": "Elo edge",
    "form_diff": "Recent form edge",
    "goal_diff_trend": "Goal-trend edge",
    "rest_days_diff": "Rest advantage",
    "confederation_gap": "Confederation-strength edge",
    "host_flag": "Host pressure edge",
}

FEATURE_UNITS = {
    "elo_diff": " Elo",
    "form_diff": " form points",
    "goal_diff_trend": " goal-trend points",
    "rest_days_diff": " days",
    "confederation_gap": " rating points",
}


class MatchPredictorService:
    def __init__(self, repository: SnapshotRepository) -> None:
        self.repository = repository

    @property
    def artifact(self) -> dict[str, Any] | None:
        return load_artifact("match_model.joblib")

    @staticmethod
    def _rounded_probabilities(home_win: float, draw: float, away_win: float) -> tuple[float, float, float]:
        rounded = [round(home_win, 4), round(draw, 4), round(away_win, 4)]
        residual = round(1.0 - sum(rounded), 4)
        if residual:
            anchor = max(range(len(rounded)), key=lambda index: rounded[index])
            rounded[anchor] = round(rounded[anchor] + residual, 4)
        return rounded[0], rounded[1], rounded[2]

    def _feature_row(self, request: MatchPredictionRequest) -> dict[str, float]:
        teams = self.repository.team_lookup()
        home = teams[request.home_team]
        away = teams[request.away_team]
        return {
            "elo_diff": float(home["elo_rating"] - away["elo_rating"]),
            "form_diff": float(home["recent_form_points"] - away["recent_form_points"]),
            "goal_diff_trend": float(home["goal_diff_trend"] - away["goal_diff_trend"]),
            "rest_days_diff": float(home["rest_days"] - away["rest_days"]),
            "confederation_gap": float(home["confed_strength"] - away["confed_strength"]),
            "host_flag": float(home["host"] or away["host"]),
        }

    @staticmethod
    def _feature_driver_text(feature_name: str, value: float, request: MatchPredictionRequest) -> str:
        if feature_name == "host_flag":
            return "Host or co-host signal is active." if value else "No host advantage is active."

        beneficiary = request.home_team if value >= 0 else request.away_team
        magnitude = abs(value)
        return f"{FEATURE_LABELS.get(feature_name, feature_name)}: {beneficiary} by {magnitude:.2f}{FEATURE_UNITS.get(feature_name, '')}."

    def _beneficiary_team(self, feature_name: str, value: float, request: MatchPredictionRequest) -> str:
        if feature_name == "host_flag":
            teams = self.repository.team_lookup()
            home_host = bool(teams[request.home_team]["host"])
            away_host = bool(teams[request.away_team]["host"])
            if home_host and not away_host:
                return request.home_team
            if away_host and not home_host:
                return request.away_team
            if home_host and away_host:
                return "Co-hosts"
            return "Neutral context"
        if value > 0:
            return request.home_team
        if value < 0:
            return request.away_team
        return "Even"

    def _factor_payload(
        self,
        artifact: dict[str, Any],
        frame: np.ndarray,
        request: MatchPredictionRequest,
        features: dict[str, float],
    ) -> tuple[list[str], list[PredictionFactor]]:
        model = artifact["model"]
        scaler = model.named_steps["scale"]
        classifier = model.named_steps["clf"]
        probabilities = model.predict_proba(frame)[0]
        predicted_index = int(probabilities.argmax())
        standardized_row = scaler.transform(frame)[0]
        coefficients = classifier.coef_[predicted_index]
        contributions = {
            feature_name: float(standardized_row[index] * coefficients[index]) for index, feature_name in enumerate(MATCH_FEATURES)
        }
        ranked = sorted(contributions.items(), key=lambda item: abs(item[1]), reverse=True)
        top_drivers = [self._feature_driver_text(feature_name, features[feature_name], request) for feature_name, _ in ranked[:3]]
        max_contribution = max((abs(value) for value in contributions.values()), default=0.0) or 1.0

        factors = [
            PredictionFactor(
                key=feature_name,
                label=FEATURE_LABELS.get(feature_name, feature_name.replace("_", " ").title()),
                edge_team=self._beneficiary_team(feature_name, features[feature_name], request),
                edge_value=round(abs(features[feature_name]), 3),
                impact_score=round(min(1.0, abs(contribution) / max_contribution), 3),
                summary=self._feature_driver_text(feature_name, features[feature_name], request),
            )
            for feature_name, contribution in ranked[:4]
        ]
        return top_drivers, factors

    @staticmethod
    def _stage_label(stage: str) -> str:
        return stage.replace("_", " ")

    def _momentum_payload(
        self,
        request: MatchPredictionRequest,
        projected_winner: str,
        home_win: float,
        draw: float,
        away_win: float,
    ) -> MomentumRead:
        edge = abs(home_win - away_win)
        pressure_bonus = 0.08 if request.stage != "group" else 0.0
        swing_index = round(min(100.0, ((edge + pressure_bonus) * 240) + (max(home_win, away_win) * 18)), 1)
        if edge >= 0.22:
            confidence_band = "Clear lean"
        elif edge >= 0.1:
            confidence_band = "Measured lean"
        else:
            confidence_band = "Knife-edge"

        if draw >= 0.28 or (request.stage != "group" and edge < 0.11):
            volatility = "High"
        elif draw >= 0.2:
            volatility = "Moderate"
        else:
            volatility = "Low"

        if confidence_band == "Knife-edge":
            summary = (
                f"The model only shows a narrow {projected_winner} edge, so match-state swings inside the "
                f"{self._stage_label(request.stage)} should matter more than a single pre-match number."
            )
        else:
            summary = (
                f"{projected_winner} enters with the stronger pre-match pulse, but {volatility.lower()} volatility "
                f"remains because draw risk sits at {draw:.0%}."
            )

        return MomentumRead(
            edge_team=projected_winner,
            swing_index=swing_index,
            confidence_band=confidence_band,
            volatility=volatility,
            summary=summary,
        )

    def _narrative(
        self,
        request: MatchPredictionRequest,
        projected_winner: str,
        draw: float,
        top_factors: list[PredictionFactor],
        momentum: MomentumRead,
    ) -> list[str]:
        factor_names = [factor.label.lower() for factor in top_factors[:2]]
        if len(factor_names) >= 2:
            lead_reason = f"{factor_names[0]} and {factor_names[1]}"
        elif factor_names:
            lead_reason = factor_names[0]
        else:
            lead_reason = "overall profile strength"

        location_note = (
            "Neutral-site assumptions mute travel and crowd noise."
            if request.neutral_site
            else "Host and travel context remain active in the read."
        )

        volatility_note = (
            f"Draw probability is {draw:.0%}, so this still projects as a live game state rather than a settled script."
            if draw >= 0.2
            else f"Draw risk is contained at {draw:.0%}, which lets the edge breathe earlier."
        )

        return [
            f"{projected_winner} owns the early edge because {lead_reason} tilt the briefing in their direction.",
            volatility_note,
            f"{location_note} That matters more once the fixture moves into the {self._stage_label(request.stage)}.",
        ]

    def predict(self, request: MatchPredictionRequest) -> MatchPredictionResponse:
        features = self._feature_row(request)
        artifact = self.artifact
        if artifact is None:
            raise ModelArtifactUnavailableError("match")

        frame = np.array([[features[feature_name] for feature_name in MATCH_FEATURES]], dtype=float)
        probabilities = artifact["model"].predict_proba(frame)[0]
        classes = list(artifact["classes"])
        lookup = {label: float(probability) for label, probability in zip(classes, probabilities, strict=True)}
        home_win = lookup.get("home", 0.0)
        draw = lookup.get("draw", 0.0)
        away_win = lookup.get("away", 0.0)
        home_win, draw, away_win = self._rounded_probabilities(home_win, draw, away_win)
        projected_winner = request.home_team if home_win >= away_win else request.away_team
        top_drivers, factors = self._factor_payload(artifact, frame, request, features)
        momentum = self._momentum_payload(request, projected_winner, home_win, draw, away_win)
        narrative = self._narrative(request, projected_winner, draw, factors, momentum)
        return MatchPredictionResponse(
            home_win_probability=home_win,
            draw_probability=draw,
            away_win_probability=away_win,
            projected_winner=projected_winner,
            model_version=artifact["version"],
            training_window=artifact["training_window"],
            sample_size=int(artifact["sample_size"]),
            mode="trained_model",
            top_drivers=top_drivers,
            factors=factors,
            momentum=momentum,
            narrative=narrative,
        )
