from world_cup_intelligence.services.elo import EloMatch, build_ratings


def test_elo_builder_rewards_wins() -> None:
    ratings = build_ratings(
        [
            EloMatch(home_team="Argentina", away_team="Mexico", home_goals=2, away_goals=0, neutral=True),
            EloMatch(home_team="Argentina", away_team="Brazil", home_goals=1, away_goals=1, neutral=True),
        ]
    )
    assert ratings["Argentina"] > ratings["Mexico"]

