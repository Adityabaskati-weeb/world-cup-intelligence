from __future__ import annotations

from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET = REPO_ROOT / "data" / "snapshots" / "international_results.csv"
RESULTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"


def fetch_international_results() -> None:
    try:
        response = requests.get(RESULTS_URL, timeout=30)
        response.raise_for_status()
    except requests.RequestException:
        if TARGET.exists():
            print(f"Skipping international results fetch: network request failed. Keeping existing snapshot at {TARGET}")
            return
        raise

    TARGET.write_text(response.text, encoding="utf-8")
    print(f"Wrote historical results to {TARGET}")


if __name__ == "__main__":
    fetch_international_results()
