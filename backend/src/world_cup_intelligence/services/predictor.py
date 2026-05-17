from __future__ import annotations

from typing import Any

import pandas as pd

from world_cup_intelligence.data.repository import SnapshotRepository
from world_cup_intelligence.schemas.api import MatchPredictionRequest, MatchPredictionResponse
from world_cup_intelligence.services.training import MATCH_FEATURES, load_artifact, softmax


class MatchPredictorService:
    def __init__(self, repository: SnapshotRepository) -> None:
        self.repository = repository
        self.artifact = load_artifact("match_model.joblib")

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

    def _heuristic(self, request: MatchPredictionRequest, features: dict[str, float]) -> MatchPredictionResponse:
        home_score = 0.65 * features["elo_diff"] / 100.0 + 0.2 * features["form_diff"] + 0.1 * features["host_flag"]
        away_score = -0.65 * features["elo_diff"] / 100.0 - 0.2 * features["form_diff"]
        draw_score = 0.2 - abs(features["elo_diff"]) / 450.0
        home_win, draw, away_win = softmax([home_score, draw_score, away_score])
        home_win, draw, away_win = self._rounded_probabilities(home_win, draw, away_win)
        projected_winner = request.home_team if home_win >= away_win else request.away_team
        drivers = [
            f"Elo edge: {request.home_team if features['elo_diff'] >= 0 else request.away_team}",
            f"Recent form edge: {request.home_team if features['form_diff'] >= 0 else request.away_team}",
            "Host indicator applied" if features["host_flag"] else "Neutral-site assumptions applied",
        ]
        return MatchPredictionResponse(
            home_win_probability=home_win,
            draw_probability=draw,
            away_win_probability=away_win,
            projected_winner=projected_winner,
            model_version="heuristic-fallback-v1",
            training_window="snapshot_priors",
            sample_size=48,
            mode="heuristic_fallback",
            top_drivers=drivers,
        )

    def predict(self, request: MatchPredictionRequest) -> MatchPredictionResponse:
        features = self._feature_row(request)
        if not self.artifact:
            return self._heuristic(request, features)

        frame = pd.DataFrame([features], columns=MATCH_FEATURES)
        probabilities = self.artifact["model"].predict_proba(frame)[0]
        classes = list(self.artifact["classes"])
        lookup = {label: float(probability) for label, probability in zip(classes, probabilities, strict=True)}
        home_win = lookup.get("home", 0.0)
        draw = lookup.get("draw", 0.0)
        away_win = lookup.get("away", 0.0)
        home_win, draw, away_win = self._rounded_probabilities(home_win, draw, away_win)
        projected_winner = request.home_team if home_win >= away_win else request.away_team
        top_drivers = [
            f"Elo diff: {features['elo_diff']:.1f}",
            f"Form diff: {features['form_diff']:.1f}",
            f"Goal trend diff: {features['goal_diff_trend']:.1f}",
        ]
        return MatchPredictionResponse(
            home_win_probability=home_win,
            draw_probability=draw,
            away_win_probability=away_win,
            projected_winner=projected_winner,
            model_version=self.artifact["version"],
            training_window=self.artifact["training_window"],
            sample_size=int(self.artifact["sample_size"]),
            mode="trained_model",
            top_drivers=top_drivers,
        )
