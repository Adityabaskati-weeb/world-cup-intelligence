from __future__ import annotations

from fetch_international_results import fetch_international_results
from fetch_tournament_snapshot import fetch_tournament_snapshot


def main() -> None:
    fetch_tournament_snapshot()
    fetch_international_results()


if __name__ == "__main__":
    main()

