import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

const apiMock = vi.hoisted(() => ({
  getHealth: vi.fn().mockResolvedValue({
    status: "ok",
    runtime_mode: "snapshot_backed_api",
    active_tournament: "world_cup_2026",
  }),
  getRefreshStatus: vi.fn().mockResolvedValue({
    overall_status: "attention",
    generated_at: "2026-05-17T10:00:00Z",
    sources: [
      {
        key: "fixture_sync",
        label: "Fixture sync",
        status: "attention",
        updated_at: "2026-05-17T10:00:00Z",
        source: "football-data.org",
        detail: "Token missing",
      },
    ],
  }),
  getTournamentCurrent: vi.fn().mockRejectedValue(new Error("Backend unavailable")),
  getFixtures: vi.fn().mockResolvedValue([
    {
      match_id: "1",
      stage: "group",
      date: "2026-06-11",
      kickoff_local: "20:00",
      venue: "Toronto Stadium",
      group: "A",
      home_team: "Canada",
      away_team: "Japan",
      status: "scheduled",
    },
  ]),
  getStandings: vi.fn().mockResolvedValue([
    {
      group: "A",
      team: "Canada",
      points: 6,
      played: 3,
      won: 2,
      drawn: 0,
      lost: 1,
      goals_for: 5,
      goals_against: 3,
      goal_difference: 2,
      rank: 1,
    },
  ]),
  getXgCatalog: vi.fn().mockResolvedValue({
    teams: [{ team_id: "brazil", label: "Brazil" }],
    players: [{ player_id: "mbappe", player_name: "Kylian Mbappe", team: "France" }],
  }),
  getTeamXg: vi.fn().mockResolvedValue({
    scope: "team",
    target_id: "brazil",
    label: "Brazil",
    team: "Brazil",
    total_xg: 6.42,
    actual_goals: 7,
    finishing_delta: 0.58,
    shots: [],
    zones: [{ zone: "central-box", shots: 12, xg: 3.18 }],
    model_version: "xg-xgboost-v3",
    training_window: "statsbomb_open_data_plus_world_cup",
    sample_size: 28,
  }),
  getPlayerXg: vi.fn().mockResolvedValue({
    scope: "player",
    target_id: "mbappe",
    label: "Kylian Mbappe",
    team: "France",
    total_xg: 2.41,
    actual_goals: 3,
    finishing_delta: 0.59,
    shots: [],
    zones: [{ zone: "central-box", shots: 3, xg: 1 }],
    model_version: "xg-xgboost-v3",
    training_window: "statsbomb_open_data_plus_world_cup",
    sample_size: 9,
  }),
}));

vi.mock("../lib/api", () => ({
  api: apiMock,
  describeError: (error: unknown) => (error instanceof Error ? error.message : "Unknown error"),
}));

import { LandingPage } from "../routes/LandingPage";
import { TournamentHub } from "../routes/TournamentHub";
import { XgExplorerPage } from "../routes/XgExplorerPage";

describe("resilience and accessibility", () => {
  it("shows a clear tournament error state when the backend request fails", async () => {
    apiMock.getTournamentCurrent.mockRejectedValueOnce(new Error("Backend unavailable"));
    render(<TournamentHub />);

    expect(await screen.findByText("Tournament data could not be loaded.")).toBeInTheDocument();
    expect(screen.getByText("Backend unavailable")).toBeInTheDocument();
  });

  it("keeps the landing experience usable when live fixture framing fails", async () => {
    apiMock.getTournamentCurrent.mockResolvedValueOnce({
      slug: "world_cup_2026",
      name: "FIFA World Cup 2026",
      start_date: "2026-06-11",
      end_date: "2026-07-19",
      host_countries: ["Canada", "Mexico", "United States"],
      host_cities: ["Toronto", "Mexico City", "New York/New Jersey"],
      format: { group_count: 12, teams_per_group: 4 },
      groups: { A: ["Canada", "Mexico", "Japan", "Morocco"] },
    });
    apiMock.getFixtures.mockRejectedValueOnce(new Error("Fixture feed offline"));

    render(
      <MemoryRouter>
        <LandingPage />
      </MemoryRouter>,
    );

    expect(await screen.findByRole("heading", { name: "Feel the tournament first. Then read the hidden game." })).toBeInTheDocument();
    expect(await screen.findByText("Live tournament context is temporarily unavailable.")).toBeInTheDocument();
    expect(screen.getByText("Fixture feed offline")).toBeInTheDocument();
  });

  it("keeps xG scope toggles accessible as users switch views", async () => {
    const user = userEvent.setup();
    render(<XgExplorerPage />);

    await waitFor(() => expect(apiMock.getTeamXg).toHaveBeenCalled());
    const teamButton = screen.getByRole("button", { name: "Team view" });
    const playerButton = screen.getByRole("button", { name: "Player view" });

    expect(teamButton).toHaveAttribute("aria-pressed", "true");
    expect(playerButton).toHaveAttribute("aria-pressed", "false");

    await user.click(playerButton);
    await waitFor(() => expect(apiMock.getPlayerXg).toHaveBeenCalled());

    expect(teamButton).toHaveAttribute("aria-pressed", "false");
    expect(playerButton).toHaveAttribute("aria-pressed", "true");
  });
});
