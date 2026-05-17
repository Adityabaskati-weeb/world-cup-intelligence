from __future__ import annotations

from random import Random

from world_cup_intelligence.data.repository import SnapshotRepository
from world_cup_intelligence.schemas.api import BracketMatch, TournamentSimulationRequest, TournamentSimulationResponse
from world_cup_intelligence.services.penalty import PenaltyService
from world_cup_intelligence.services.tournament import NEXT_ROUNDS, ROUND_OF_32_TEMPLATE, TournamentService


class SimulationService:
    def __init__(self, repository: SnapshotRepository) -> None:
        self.repository = repository
        self.tournament = TournamentService(repository)
        self.penalty = PenaltyService(repository)

    def _team_strength(self, team_name: str) -> float:
        profile = self.repository.team_lookup()[team_name]
        return profile["elo_rating"] + (profile["recent_form_points"] * 20)

    def _resolve_match(self, rng: Random, home_team: str, away_team: str) -> tuple[str, str]:
        home_strength = self._team_strength(home_team)
        away_strength = self._team_strength(away_team)
        delta = home_strength - away_strength
        noise = rng.uniform(-80, 80)
        adjusted = delta + noise
        if abs(adjusted) < 30:
            kickers = self.repository.penalty_profiles()["kickers"]
            keepers = self.repository.penalty_profiles()["keepers"]
            home_kicker = kickers[0]["player_id"]
            away_kicker = kickers[-1]["player_id"]
            home_keeper = keepers[0]["keeper_id"]
            away_keeper = keepers[-1]["keeper_id"]
            home_probability = self.penalty.predict(
                request=self._penalty_request(home_kicker, away_keeper, pressure=0.85)
            ).scoring_probability
            away_probability = self.penalty.predict(
                request=self._penalty_request(away_kicker, home_keeper, pressure=0.85)
            ).scoring_probability
            winner = home_team if home_probability >= away_probability else away_team
            return winner, "penalties"
        winner = home_team if adjusted >= 0 else away_team
        return winner, "regulation"

    @staticmethod
    def _penalty_request(player_id: str, keeper_id: str, pressure: float):
        from world_cup_intelligence.schemas.api import PenaltyPredictionRequest

        return PenaltyPredictionRequest(player_id=player_id, keeper_id=keeper_id, context={"pressure": pressure})

    def simulate(self, request: TournamentSimulationRequest) -> TournamentSimulationResponse:
        rng = Random(request.seed)
        top_two = {team.slot: team.team for team in self.tournament.top_two()}
        third_place = self.tournament.best_third_place()
        third_assignments = self.tournament.resolve_third_place_slots(third_place)

        winners: dict[str, str] = {}
        round_of_32: list[BracketMatch] = []
        for match in ROUND_OF_32_TEMPLATE:
            home_team = top_two.get(match["home_slot"], match["home_slot"])
            away_slot = match["away_slot"]
            if away_slot.startswith("3"):
                away_team = third_assignments[match["match_id"]].team
            else:
                away_team = top_two.get(away_slot, away_slot)
            winner, resolution = self._resolve_match(rng, home_team, away_team)
            winners[f"W{match['match_id']}"] = winner
            round_of_32.append(
                BracketMatch(
                    match_id=match["match_id"],
                    stage="round_of_32",
                    venue=match["venue"],
                    slot_home=match["home_slot"],
                    slot_away=match["away_slot"],
                    home_team=home_team,
                    away_team=away_team,
                    winner=winner,
                    resolution=resolution,
                )
            )

        staged_rounds: dict[str, list[BracketMatch]] = {}
        for stage_name in ["round_of_16", "quarterfinal", "semifinal"]:
            staged_rounds[stage_name] = []
            for match in NEXT_ROUNDS[stage_name]:
                home_team = winners[match["home_slot"]]
                away_team = winners[match["away_slot"]]
                winner, resolution = self._resolve_match(rng, home_team, away_team)
                winners[f"W{match['match_id']}"] = winner
                staged_rounds[stage_name].append(
                    BracketMatch(
                        match_id=match["match_id"],
                        stage=stage_name,
                        venue=match["venue"],
                        slot_home=match["home_slot"],
                        slot_away=match["away_slot"],
                        home_team=home_team,
                        away_team=away_team,
                        winner=winner,
                        resolution=resolution,
                    )
                )

        final_def = NEXT_ROUNDS["final"][0]
        final_home = winners[final_def["home_slot"]]
        final_away = winners[final_def["away_slot"]]
        champion, final_resolution = self._resolve_match(rng, final_home, final_away)
        final = BracketMatch(
            match_id=final_def["match_id"],
            stage="final",
            venue=final_def["venue"],
            slot_home=final_def["home_slot"],
            slot_away=final_def["away_slot"],
            home_team=final_home,
            away_team=final_away,
            winner=champion,
            resolution=final_resolution,
        )
        return TournamentSimulationResponse(
            qualified_third_place=[team.team for team in third_place],
            round_of_32=round_of_32,
            round_of_16=staged_rounds["round_of_16"],
            quarterfinals=staged_rounds["quarterfinal"],
            semifinals=staged_rounds["semifinal"],
            final=final,
            champion=champion,
        )

