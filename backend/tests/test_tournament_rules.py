from world_cup_intelligence.data.repository import SnapshotRepository
from world_cup_intelligence.services.tournament import TournamentService


def test_best_third_place_selection_returns_eight_teams() -> None:
    service = TournamentService(SnapshotRepository())
    thirds = service.best_third_place()
    assert len(thirds) == 8
    assert all(team.slot.startswith("3") for team in thirds)


def test_third_place_slot_assignment_is_unique() -> None:
    service = TournamentService(SnapshotRepository())
    thirds = service.best_third_place()
    allocation = service.resolve_third_place_slots(thirds)
    assigned_groups = [team.group for team in allocation.values()]
    assert len(assigned_groups) == len(set(assigned_groups))

