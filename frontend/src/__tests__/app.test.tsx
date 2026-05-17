import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../App";

vi.mock("../lib/api", () => ({
  api: {
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
    getTournamentCurrent: vi.fn().mockResolvedValue({
      slug: "world_cup_2026",
      name: "FIFA World Cup 2026",
      start_date: "2026-06-11",
      end_date: "2026-07-19",
      host_countries: ["Canada", "Mexico", "United States"],
      host_cities: ["Toronto", "Mexico City", "New York/New Jersey"],
      format: { group_count: 12, teams_per_group: 4 },
      groups: {
        A: ["Canada", "Mexico", "United States", "Japan"],
      },
    }),
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
  },
  describeError: (error: unknown) => (error instanceof Error ? error.message : "Unknown error"),
}));

describe("App shell", () => {
  it("renders the global navigation and the landing experience", async () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );

    expect(screen.getByText("Matchflow")).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Feel the tournament first. Then read the hidden game." })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Home" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Tournament Hub" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Match Predictor" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "xG Explorer" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Penalty Lab" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Dark" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Light" })).toBeInTheDocument();
  });
});
