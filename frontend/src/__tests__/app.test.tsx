import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../App";

vi.mock("../lib/api", () => ({
  api: {
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
    getFixtures: vi.fn().mockResolvedValue([]),
    getStandings: vi.fn().mockResolvedValue([]),
    simulateTournament: vi.fn().mockResolvedValue(null),
  },
}));

describe("App shell", () => {
  it("renders the global navigation", () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "World Cup Intelligence 2026" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Tournament Hub" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Match Predictor" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "xG Explorer" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Penalty Lab" })).toBeInTheDocument();
  });
});
