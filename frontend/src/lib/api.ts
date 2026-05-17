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

export type XgCatalogTeam = {
  team_id: string;
  label: string;
};

export type KickerProfile = {
  player_id: string;
  player_name: string;
  team?: string;
  preferred_foot?: string;
};

export type KeeperProfile = {
  keeper_id: string;
  keeper_name: string;
  team?: string;
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
  factors: PredictionFactor[];
  momentum: MomentumRead;
  narrative: string[];
};

export type PredictionFactor = {
  key: string;
  label: string;
  edge_team: string;
  edge_value: number;
  impact_score: number;
  summary: string;
};

export type MomentumRead = {
  edge_team: string;
  swing_index: number;
  confidence_band: string;
  volatility: string;
  summary: string;
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

export type RuntimeMode = "live_api" | "snapshot_backed_api";

export type HealthResponse = {
  status: string;
  runtime_mode: RuntimeMode;
  active_tournament: string;
};

export type RefreshSourceStatus = {
  key: string;
  label: string;
  status: "live" | "snapshot" | "attention" | string;
  updated_at?: string | null;
  source?: string | null;
  detail: string;
};

export type RefreshStatus = {
  overall_status: "live" | "snapshot" | "attention" | string;
  generated_at: string;
  sources: RefreshSourceStatus[];
};

type PlayersPayload = {
  players: PlayerProfile[];
  kickers: KickerProfile[];
  keepers: KeeperProfile[];
};

type ValidationErrorItem = {
  loc?: Array<string | number>;
  msg?: string;
};

function normalizeApiBase(base: string): string {
  return base.endsWith("/") ? base.slice(0, -1) : base;
}

function inferApiBase(): string {
  const configuredApiBase = import.meta.env.VITE_API_BASE_URL?.trim();
  if (configuredApiBase) {
    return normalizeApiBase(configuredApiBase);
  }

  if (typeof window === "undefined") {
    return "";
  }

  const host = window.location.hostname;
  if (host === "127.0.0.1" || host === "localhost") {
    return "http://127.0.0.1:8000";
  }

  return "";
}

const resolvedApiBase = inferApiBase();

function apiUrl(path: string): string {
  return resolvedApiBase ? `${resolvedApiBase}${path}` : path;
}

function formatValidationErrors(detail: unknown): string | null {
  if (!Array.isArray(detail)) {
    return null;
  }

  const messages = detail
    .map((item) => {
      const typed = item as ValidationErrorItem;
      if (!typed.msg) {
        return null;
      }
      const path = typed.loc?.filter((segment) => segment !== "body").join(" -> ");
      return path ? `${path}: ${typed.msg}` : typed.msg;
    })
    .filter((message): message is string => Boolean(message));

  return messages.length ? messages.join(" | ") : null;
}

async function extractErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.clone().json()) as { detail?: unknown; message?: unknown };
    const validationMessage = formatValidationErrors(payload.detail);
    if (validationMessage) {
      return validationMessage;
    }
    if (typeof payload.detail === "string" && payload.detail.trim()) {
      return payload.detail;
    }
    if (typeof payload.message === "string" && payload.message.trim()) {
      return payload.message;
    }
  } catch {
    // Fall back to the plain response body below.
  }

  const body = await response.text().catch(() => "");
  if (body.trim()) {
    return body.trim();
  }

  return `Request failed with status ${response.status}.`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(apiUrl(path), {
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      ...init,
    });
  } catch {
    throw new Error("Could not reach the Matchflow API. Start the backend or verify VITE_API_BASE_URL.");
  }

  if (!response.ok) {
    const message = await extractErrorMessage(response);
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export const api = {
  getHealth: () => request<HealthResponse>("/api/health"),
  getRefreshStatus: () => request<RefreshStatus>("/api/refresh/status"),
  getTournamentCurrent: () => request<TournamentCurrent>("/api/tournament/current"),
  getFixtures: async () => (await request<{ fixtures: Fixture[] }>("/api/fixtures")).fixtures,
  getStandings: () => request<Standing[]>("/api/standings"),
  getTeams: async () => (await request<{ teams: TeamProfile[] }>("/api/teams")).teams,
  getPlayers: () => request<PlayersPayload>("/api/players"),
  getXgCatalog: () => request<{ teams: XgCatalogTeam[]; players: PlayerProfile[] }>("/api/xg/catalog"),
  predictMatch: (payload: { home_team: string; away_team: string; neutral_site: boolean; stage: string }) =>
    request<MatchPrediction>("/api/predict/match", { method: "POST", body: JSON.stringify(payload) }),
  getTeamXg: (teamId: string) => request<XgProfile>(`/api/xg/team/${teamId}`),
  getPlayerXg: (playerId: string) => request<XgProfile>(`/api/xg/player/${playerId}`),
  predictPenalty: (payload: { player_id: string; keeper_id: string; context: Record<string, unknown> }) =>
    request<PenaltyPrediction>("/api/predict/penalty", { method: "POST", body: JSON.stringify(payload) }),
  simulateTournament: (seed = 2026) =>
    request<TournamentSimulation>("/api/simulate/tournament", { method: "POST", body: JSON.stringify({ seed }) }),
};

export function describeError(error: unknown): string {
  if (error instanceof Error && error.message) {
    if (error.message.includes("Failed to fetch")) {
      return "Could not reach the Matchflow API. Start the backend or verify VITE_API_BASE_URL.";
    }
    return error.message;
  }
  return "Something went wrong while loading this Matchflow surface.";
}
