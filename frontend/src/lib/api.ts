export type TournamentCurrent = {
  slug: string;
  name: string;
  start_date: string;
  end_date: string;
  host_countries: string[];
  host_cities: string[];
  format: { group_count: number; teams_per_group: number };
  groups: Record<string, string[]>;
};

export type Fixture = {
  match_id: string;
  stage: string;
  date: string;
  kickoff_local: string;
  venue: string;
  group: string | null;
  home_team: string;
  away_team: string;
  status: string;
};

export type Standing = {
  group: string;
  team: string;
  points: number;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  rank: number;
};

export type TeamProfile = {
  team_id: string;
  name: string;
  group: string;
  confederation: string;
  host: boolean;
};

export type PlayerProfile = {
  player_id: string;
  player_name: string;
  team: string;
};

export type KeeperProfile = {
  keeper_id: string;
  keeper_name: string;
};

export type MatchPrediction = {
  home_win_probability: number;
  draw_probability: number;
  away_win_probability: number;
  projected_winner: string;
  model_version: string;
  training_window: string;
  sample_size: number;
  mode: string;
  top_drivers: string[];
};

export type XgPoint = {
  player_id: string;
  player_name: string;
  minute: number;
  x: number;
  y: number;
  xg: number;
  outcome: string;
  body_part: string;
  situation: string;
};

export type XgProfile = {
  scope: string;
  target_id: string;
  label: string;
  team: string;
  total_xg: number;
  actual_goals: number;
  finishing_delta: number;
  shots: XgPoint[];
  zones: { zone: string; shots: number; xg: number }[];
  model_version: string;
  training_window: string;
  sample_size: number;
};

export type PenaltyPrediction = {
  player_id: string;
  keeper_id: string;
  scoring_probability: number;
  likely_target_zone: string;
  target_zone_probabilities: Record<string, number>;
  model_version: string;
  training_window: string;
  sample_size: number;
  notes: string[];
};

export type BracketMatch = {
  match_id: string;
  stage: string;
  venue: string;
  slot_home: string;
  slot_away: string;
  home_team?: string;
  away_team?: string;
  winner?: string;
  resolution?: string;
};

export type TournamentSimulation = {
  qualified_third_place: string[];
  round_of_32: BracketMatch[];
  round_of_16: BracketMatch[];
  quarterfinals: BracketMatch[];
  semifinals: BracketMatch[];
  final: BracketMatch;
  champion: string;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export const api = {
  getTournamentCurrent: () => request<TournamentCurrent>("/api/tournament/current"),
  getFixtures: async () => (await request<{ fixtures: Fixture[] }>("/api/fixtures")).fixtures,
  getStandings: () => request<Standing[]>("/api/standings"),
  getTeams: async () => (await request<{ teams: TeamProfile[] }>("/api/teams")).teams,
  getPlayers: () => request<{ players: PlayerProfile[]; keepers: KeeperProfile[] }>("/api/players"),
  predictMatch: (payload: { home_team: string; away_team: string; neutral_site: boolean; stage: string }) =>
    request<MatchPrediction>("/api/predict/match", { method: "POST", body: JSON.stringify(payload) }),
  getTeamXg: (teamId: string) => request<XgProfile>(`/api/xg/team/${teamId}`),
  getPlayerXg: (playerId: string) => request<XgProfile>(`/api/xg/player/${playerId}`),
  predictPenalty: (payload: { player_id: string; keeper_id: string; context: Record<string, unknown> }) =>
    request<PenaltyPrediction>("/api/predict/penalty", { method: "POST", body: JSON.stringify(payload) }),
  simulateTournament: (seed = 2026) =>
    request<TournamentSimulation>("/api/simulate/tournament", { method: "POST", body: JSON.stringify({ seed }) }),
};

