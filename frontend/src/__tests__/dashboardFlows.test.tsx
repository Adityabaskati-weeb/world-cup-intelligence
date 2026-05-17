import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
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
        key: "tournament_reference",
        label: "Tournament reference",
        status: "snapshot",
        updated_at: "2026-05-17",
        source: "FIFA + config snapshot",
        detail: "12 groups and 36 fixtures are cached from the 2026 tournament reference layer.",
      },
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
    groups: { A: ["Canada", "Mexico", "Japan", "Morocco"] },
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
  simulateTournament: vi.fn().mockResolvedValue({
    qualified_third_place: ["Mexico"],
    round_of_32: [
      {
        match_id: "73",
        stage: "round_of_32",
        venue: "Los Angeles Stadium",
        slot_home: "1A",
        slot_away: "2B",
        home_team: "Canada",
        away_team: "Mexico",
        winner: "Canada",
        resolution: "regulation",
      },
    ],
    round_of_16: [],
    quarterfinals: [],
    semifinals: [],
    final: {
      match_id: "104",
      stage: "final",
      venue: "MetLife Stadium",
      slot_home: "W101",
      slot_away: "W102",
      home_team: "Canada",
      away_team: "Brazil",
      winner: "Brazil",
      resolution: "penalties",
    },
    champion: "Brazil",
  }),
  getTeams: vi.fn().mockResolvedValue([
    { team_id: "mexico", name: "Mexico", group: "A", confederation: "CONCACAF", host: true },
    { team_id: "japan", name: "Japan", group: "A", confederation: "AFC", host: false },
  ]),
  predictMatch: vi.fn().mockResolvedValue({
    home_win_probability: 0.54,
    draw_probability: 0.23,
    away_win_probability: 0.23,
    projected_winner: "Mexico",
    model_version: "match-logreg-v3",
    training_window: "last_10_years",
    sample_size: 24,
    mode: "trained_model",
    top_drivers: ["Elo diff: 22.0", "Form diff: 0.8", "Goal trend diff: 0.5"],
    factors: [
      {
        key: "elo_diff",
        label: "Elo edge",
        edge_team: "Mexico",
        edge_value: 22,
        impact_score: 1,
        summary: "Elo edge: Mexico by 22.00 Elo.",
      },
    ],
    momentum: {
      edge_team: "Mexico",
      swing_index: 76,
      confidence_band: "Measured lean",
      volatility: "Moderate",
      summary: "Mexico enters with the stronger pre-match pulse.",
    },
    narrative: [
      "Mexico owns the early edge because Elo edge tilts the briefing in their direction.",
      "Draw probability is 23%, so this still projects as a live game state rather than a settled script.",
      "Host and travel context remain active in the read.",
    ],
  }),
  getXgCatalog: vi.fn().mockResolvedValue({
    teams: [
      { team_id: "argentina", label: "Argentina" },
      { team_id: "brazil", label: "Brazil" },
    ],
    players: [
      { player_id: "mbappe", player_name: "Kylian Mbappe", team: "France" },
      { player_id: "rodrygo", player_name: "Rodrygo", team: "Brazil" },
    ],
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
    model_version: "snapshot-xg-view-v1",
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
    model_version: "snapshot-xg-view-v1",
    training_window: "statsbomb_open_data_plus_world_cup",
    sample_size: 9,
  }),
  getPlayers: vi.fn().mockResolvedValue({
    players: [{ player_id: "mbappe", player_name: "Kylian Mbappe", team: "France" }],
    kickers: [{ player_id: "harry-kane", player_name: "Harry Kane", team: "England", preferred_foot: "right" }],
    keepers: [{ keeper_id: "emiliano-martinez", keeper_name: "Emiliano Martinez", team: "Argentina" }],
  }),
  predictPenalty: vi.fn().mockResolvedValue({
    player_id: "harry-kane",
    keeper_id: "emiliano-martinez",
    scoring_probability: 0.81,
    likely_target_zone: "low-right",
    target_zone_probabilities: { "low-right": 0.41, "low-left": 0.18 },
    model_version: "penalty-profile-v1",
    training_window: "major_tournaments_open_data",
    sample_size: 18,
    notes: ["Harry Kane prefers low-right.", "Pressure adjustment applied from request context."],
  }),
}));

vi.mock("../lib/api", () => ({
  api: apiMock,
  describeError: (error: unknown) => (error instanceof Error ? error.message : "Unknown error"),
}));

afterEach(() => {
  cleanup();
});

import { MatchPredictorPage } from "../routes/MatchPredictorPage";
import { PenaltyLabPage } from "../routes/PenaltyLabPage";
import { TournamentHub } from "../routes/TournamentHub";
import { XgExplorerPage } from "../routes/XgExplorerPage";

describe("dashboard flows", () => {
  it("renders the full tournament hub and runs a simulation", async () => {
    const user = userEvent.setup();
    render(<TournamentHub />);

    expect(await screen.findByText("FIFA World Cup 2026")).toBeInTheDocument();
    expect(screen.getByText("Tournament watchlist")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Simulate bracket" }));

    expect(await screen.findByText(/Champion: Brazil/i)).toBeInTheDocument();
    expect(apiMock.simulateTournament).toHaveBeenCalled();
  });

  it("submits a match prediction and shows top drivers", async () => {
    const user = userEvent.setup();
    render(<MatchPredictorPage />);

    await waitFor(() => expect(apiMock.getTeams).toHaveBeenCalled());
    await user.click(screen.getByRole("button", { name: "Run prediction" }));

    expect(await screen.findByText("Mexico edge")).toBeInTheDocument();
    expect(screen.getByText("Momentum read")).toBeInTheDocument();
    expect(screen.getByText(/Mexico owns the early edge/i)).toBeInTheDocument();
  });

  it("blocks same-team matchups before the request leaves the browser", async () => {
    const user = userEvent.setup();
    render(<MatchPredictorPage />);

    await waitFor(() => expect(apiMock.getTeams).toHaveBeenCalled());
    await user.selectOptions(screen.getByLabelText("Away team"), "Mexico");

    expect(screen.getByText("Choose two different teams before running the prediction.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Run prediction" })).toBeDisabled();
  });

  it("loads xG and penalty dashboards with connected selectors", async () => {
    const user = userEvent.setup();

    render(<XgExplorerPage />);
    expect(await screen.findByRole("heading", { name: "Brazil" })).toBeInTheDocument();
    expect(screen.getByText("central-box")).toBeInTheDocument();
    expect(screen.getByText("Football reading")).toBeInTheDocument();
    expect(screen.getByText("2 tracked teams | 2 tracked player profiles")).toBeInTheDocument();

    render(<PenaltyLabPage />);
    await waitFor(() => expect(apiMock.getPlayers).toHaveBeenCalled());
    expect(screen.getByText("1 tracked kickers | 1 tracked keepers")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Compare matchup" }));

    expect(await screen.findByText("Penalty matchup outlook")).toBeInTheDocument();
    expect(screen.getByText("Duel reading")).toBeInTheDocument();
    expect(screen.getAllByText("low-right").length).toBeGreaterThan(0);
  });
});
