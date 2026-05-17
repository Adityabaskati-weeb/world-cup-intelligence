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

export type KickerProfile = {
  player_id: string;
  player_name: string;
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

type DemoTournamentTeam = TeamProfile & {
  elo_rating: number;
  recent_form_points: number;
  goal_diff_trend: number;
  rest_days: number;
  confed_strength: number;
  projected_points: number;
  projected_won: number;
  projected_drawn: number;
  projected_lost: number;
  projected_goals_for: number;
  projected_goals_against: number;
  projected_goal_difference: number;
};

type DemoTournamentSnapshot = {
  slug: string;
  name: string;
  updated_at: string;
  groups: Record<string, string[]>;
  fixtures: Fixture[];
  teams: DemoTournamentTeam[];
};

type DemoXgTeamProfile = {
  team_id: string;
  label: string;
  total_xg: number;
  actual_goals: number;
  sample_size: number;
  zones: { zone: string; shots: number; xg: number }[];
  shots: XgPoint[];
};

type DemoXgPlayerProfile = PlayerProfile & {
  total_xg: number;
  actual_goals: number;
  sample_size: number;
  zones: { zone: string; shots: number; xg: number }[];
  shots: XgPoint[];
};

type DemoXgSnapshot = {
  teams: DemoXgTeamProfile[];
  players: DemoXgPlayerProfile[];
};

type DemoPenaltyKicker = KickerProfile & {
  preferred_zone: string;
  conversion_rate: number;
  sample_size: number;
  target_zone_probabilities: Record<string, number>;
};

type DemoPenaltyKeeper = KeeperProfile & {
  save_rate: number;
  save_bias: Record<string, number>;
};

type DemoPenaltySnapshot = {
  kickers: DemoPenaltyKicker[];
  keepers: DemoPenaltyKeeper[];
};

type DemoBundle = {
  tournament: DemoTournamentSnapshot;
  xg: DemoXgSnapshot;
  penalty: DemoPenaltySnapshot;
};

type QualifiedTeam = {
  slot: string;
  team: string;
  group: string;
  points: number;
  goal_difference: number;
  goals_for: number;
};

const configuredApiBase = import.meta.env.VITE_API_BASE_URL?.trim();
const appBase = import.meta.env.BASE_URL ?? "/";
const demoOnlyMode = configuredApiBase === "demo";

const DEMO_TOURNAMENT_META: Omit<TournamentCurrent, "groups"> = {
  slug: "world_cup_2026",
  name: "FIFA World Cup 2026",
  start_date: "2026-06-11",
  end_date: "2026-07-19",
  host_countries: ["Canada", "Mexico", "United States"],
  host_cities: [
    "Toronto",
    "Vancouver",
    "Guadalajara",
    "Mexico City",
    "Monterrey",
    "Atlanta",
    "Boston",
    "Dallas",
    "Houston",
    "Kansas City",
    "Los Angeles",
    "Miami",
    "New York New Jersey",
    "Philadelphia",
    "San Francisco Bay Area",
    "Seattle",
  ],
  format: { group_count: 12, teams_per_group: 4 },
};

const ROUND_OF_32_TEMPLATE = [
  { match_id: "73", stage: "round_of_32", home_slot: "2A", away_slot: "2B", venue: "Los Angeles Stadium" },
  { match_id: "74", stage: "round_of_32", home_slot: "1E", away_slot: "3ABCDF", venue: "Boston Stadium" },
  { match_id: "75", stage: "round_of_32", home_slot: "1F", away_slot: "2C", venue: "Estadio Monterrey" },
  { match_id: "76", stage: "round_of_32", home_slot: "1C", away_slot: "2F", venue: "Houston Stadium" },
  { match_id: "77", stage: "round_of_32", home_slot: "1I", away_slot: "3CDFGH", venue: "New York New Jersey Stadium" },
  { match_id: "78", stage: "round_of_32", home_slot: "2E", away_slot: "2I", venue: "Dallas Stadium" },
  { match_id: "79", stage: "round_of_32", home_slot: "1A", away_slot: "3CEFHI", venue: "Mexico City Stadium" },
  { match_id: "80", stage: "round_of_32", home_slot: "1L", away_slot: "3EHIJK", venue: "Atlanta Stadium" },
  { match_id: "81", stage: "round_of_32", home_slot: "1D", away_slot: "3BEFIJ", venue: "San Francisco Bay Area Stadium" },
  { match_id: "82", stage: "round_of_32", home_slot: "1G", away_slot: "3AEHIJ", venue: "Seattle Stadium" },
  { match_id: "83", stage: "round_of_32", home_slot: "2K", away_slot: "2L", venue: "Toronto Stadium" },
  { match_id: "84", stage: "round_of_32", home_slot: "1H", away_slot: "2J", venue: "Los Angeles Stadium" },
  { match_id: "85", stage: "round_of_32", home_slot: "1B", away_slot: "3EFGIJ", venue: "BC Place Vancouver" },
  { match_id: "86", stage: "round_of_32", home_slot: "1J", away_slot: "2H", venue: "Miami Stadium" },
  { match_id: "87", stage: "round_of_32", home_slot: "1K", away_slot: "3DEIJL", venue: "Kansas City Stadium" },
  { match_id: "88", stage: "round_of_32", home_slot: "2D", away_slot: "2G", venue: "Dallas Stadium" },
] as const;

const NEXT_ROUNDS = {
  round_of_16: [
    { match_id: "89", venue: "Philadelphia Stadium", home_slot: "W74", away_slot: "W77" },
    { match_id: "90", venue: "Houston Stadium", home_slot: "W73", away_slot: "W75" },
    { match_id: "91", venue: "New York New Jersey Stadium", home_slot: "W76", away_slot: "W78" },
    { match_id: "92", venue: "Mexico City Stadium", home_slot: "W79", away_slot: "W80" },
    { match_id: "93", venue: "Dallas Stadium", home_slot: "W83", away_slot: "W84" },
    { match_id: "94", venue: "Seattle Stadium", home_slot: "W81", away_slot: "W82" },
    { match_id: "95", venue: "Atlanta Stadium", home_slot: "W86", away_slot: "W88" },
    { match_id: "96", venue: "BC Place Vancouver", home_slot: "W85", away_slot: "W87" },
  ],
  quarterfinal: [
    { match_id: "97", venue: "Boston Stadium", home_slot: "W89", away_slot: "W90" },
    { match_id: "98", venue: "Los Angeles Stadium", home_slot: "W93", away_slot: "W94" },
    { match_id: "99", venue: "Miami Stadium", home_slot: "W91", away_slot: "W92" },
    { match_id: "100", venue: "Kansas City Stadium", home_slot: "W95", away_slot: "W96" },
  ],
  semifinal: [
    { match_id: "101", venue: "Dallas Stadium", home_slot: "W97", away_slot: "W98" },
    { match_id: "102", venue: "Atlanta Stadium", home_slot: "W99", away_slot: "W100" },
  ],
  final: [
    { match_id: "104", venue: "MetLife Stadium", home_slot: "W101", away_slot: "W102" },
  ],
} as const;

function normalizeApiBase(base: string): string {
  return base.endsWith("/") ? base.slice(0, -1) : base;
}

function apiUrl(path: string): string {
  if (!configuredApiBase || demoOnlyMode) {
    return path;
  }
  return `${normalizeApiBase(configuredApiBase)}${path}`;
}

function publicAssetUrl(path: string): string {
  return `${appBase}${path.replace(/^\/+/, "")}`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(apiUrl(path), {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

async function requestDemo<T>(path: string): Promise<T> {
  const response = await fetch(publicAssetUrl(path));
  if (!response.ok) {
    throw new Error(`Demo asset missing: ${path}`);
  }
  return response.json() as Promise<T>;
}

let backendAvailablePromise: Promise<boolean> | undefined;
let demoBundlePromise: Promise<DemoBundle> | undefined;

async function isBackendAvailable(): Promise<boolean> {
  if (demoOnlyMode) {
    return false;
  }
  if (!backendAvailablePromise) {
    backendAvailablePromise = request<{ status: string }>("/api/health")
      .then((payload) => payload.status === "ok")
      .catch(() => false);
  }
  return backendAvailablePromise;
}

async function withDemoFallback<T>(remote: () => Promise<T>, local: () => Promise<T>): Promise<T> {
  if (demoOnlyMode) {
    return local();
  }

  if (await isBackendAvailable()) {
    try {
      return await remote();
    } catch {
      return local();
    }
  }

  return local();
}

async function loadDemoBundle(): Promise<DemoBundle> {
  if (!demoBundlePromise) {
    demoBundlePromise = Promise.all([
      requestDemo<DemoTournamentSnapshot>("demo/tournaments/world_cup_2026.json"),
      requestDemo<DemoXgSnapshot>("demo/players/xg_profiles.json"),
      requestDemo<DemoPenaltySnapshot>("demo/players/penalty_profiles.json"),
    ]).then(([tournament, xg, penalty]) => ({ tournament, xg, penalty }));
  }
  return demoBundlePromise;
}

function buildStandings(snapshot: DemoTournamentSnapshot): Standing[] {
  const teamLookup = new Map(snapshot.teams.map((team) => [team.name, team]));
  return Object.keys(snapshot.groups)
    .sort()
    .flatMap((group) => {
      const ranked = [...snapshot.groups[group]].sort((left, right) => {
        const leftProfile = teamLookup.get(left)!;
        const rightProfile = teamLookup.get(right)!;
        return (
          rightProfile.projected_points - leftProfile.projected_points ||
          rightProfile.projected_goal_difference - leftProfile.projected_goal_difference ||
          rightProfile.projected_goals_for - leftProfile.projected_goals_for ||
          left.localeCompare(right)
        );
      });

      return ranked.map((teamName, index) => {
        const profile = teamLookup.get(teamName)!;
        return {
          group,
          team: teamName,
          points: profile.projected_points,
          played: 3,
          won: profile.projected_won,
          drawn: profile.projected_drawn,
          lost: profile.projected_lost,
          goals_for: profile.projected_goals_for,
          goals_against: profile.projected_goals_against,
          goal_difference: profile.projected_goal_difference,
          rank: index + 1,
        };
      });
    });
}

function buildTournamentCurrent(snapshot: DemoTournamentSnapshot): TournamentCurrent {
  return {
    ...DEMO_TOURNAMENT_META,
    groups: snapshot.groups,
  };
}

function buildTeamProfiles(snapshot: DemoTournamentSnapshot): TeamProfile[] {
  return snapshot.teams.map(({ team_id, name, group, confederation, host }) => ({
    team_id,
    name,
    group,
    confederation,
    host,
  }));
}

function buildPlayerPayload(bundle: DemoBundle): {
  players: PlayerProfile[];
  kickers: KickerProfile[];
  keepers: KeeperProfile[];
} {
  return {
    players: bundle.xg.players.map(({ player_id, player_name, team }) => ({ player_id, player_name, team })),
    kickers: bundle.penalty.kickers.map(({ player_id, player_name }) => ({ player_id, player_name })),
    keepers: bundle.penalty.keepers.map(({ keeper_id, keeper_name }) => ({ keeper_id, keeper_name })),
  };
}

function softmax(scores: number[]): number[] {
  const anchor = Math.max(...scores);
  const exponents = scores.map((score) => Math.exp(score - anchor));
  const total = exponents.reduce((sum, value) => sum + value, 0);
  return exponents.map((value) => value / total);
}

function roundProbabilities(home: number, draw: number, away: number): [number, number, number] {
  const rounded = [Number(home.toFixed(4)), Number(draw.toFixed(4)), Number(away.toFixed(4))];
  const residual = Number((1 - rounded.reduce((sum, value) => sum + value, 0)).toFixed(4));
  if (residual) {
    const anchor = rounded.indexOf(Math.max(...rounded));
    rounded[anchor] = Number((rounded[anchor] + residual).toFixed(4));
  }
  return [rounded[0], rounded[1], rounded[2]];
}

function createSeededRng(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state += 0x6d2b79f5;
    let value = Math.imul(state ^ (state >>> 15), state | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

function resolveTopTwo(standings: Standing[], groups: Record<string, string[]>): QualifiedTeam[] {
  return Object.keys(groups)
    .sort()
    .flatMap((group) =>
      standings
        .filter((row) => row.group === group)
        .sort((left, right) => left.rank - right.rank)
        .slice(0, 2)
        .map((row, index) => ({
          slot: `${index + 1}${group}`,
          team: row.team,
          group,
          points: row.points,
          goal_difference: row.goal_difference,
          goals_for: row.goals_for,
        })),
    );
}

function resolveBestThirdPlace(standings: Standing[], groups: Record<string, string[]>): QualifiedTeam[] {
  return Object.keys(groups)
    .sort()
    .map((group) => standings.filter((row) => row.group === group).sort((left, right) => left.rank - right.rank)[2])
    .sort(
      (left, right) =>
        right.points - left.points ||
        right.goal_difference - left.goal_difference ||
        right.goals_for - left.goals_for ||
        left.team.localeCompare(right.team),
    )
    .slice(0, 8)
    .map((row) => ({
      slot: `3${row.group}`,
      team: row.team,
      group: row.group,
      points: row.points,
      goal_difference: row.goal_difference,
      goals_for: row.goals_for,
    }));
}

function resolveThirdPlaceSlots(teams: QualifiedTeam[]): Record<string, QualifiedTeam> {
  const byGroup = new Map(teams.map((team) => [team.group, team]));
  const thirdPlaceMatches = ROUND_OF_32_TEMPLATE.filter((match) => match.away_slot.startsWith("3"));
  const assignment = new Map<string, QualifiedTeam>();
  const usedGroups = new Set<string>();
  const orderedMatches = [...thirdPlaceMatches].sort((left, right) => left.away_slot.length - right.away_slot.length);

  const backtrack = (index: number): boolean => {
    if (index === orderedMatches.length) {
      return true;
    }

    const match = orderedMatches[index];
    const eligibleGroups = match.away_slot
      .slice(1)
      .split("")
      .filter((group) => byGroup.has(group) && !usedGroups.has(group))
      .sort((left, right) => teams.findIndex((team) => team.group === left) - teams.findIndex((team) => team.group === right));

    for (const group of eligibleGroups) {
      const team = byGroup.get(group)!;
      assignment.set(match.match_id, team);
      usedGroups.add(group);
      if (backtrack(index + 1)) {
        return true;
      }
      assignment.delete(match.match_id);
      usedGroups.delete(group);
    }

    return false;
  };

  if (!backtrack(0)) {
    throw new Error("Could not resolve third-place bracket slots.");
  }

  return Object.fromEntries(assignment);
}

function buildXgProfile(
  scope: "team" | "player",
  targetId: string,
  label: string,
  team: string,
  totalXg: number,
  actualGoals: number,
  zones: { zone: string; shots: number; xg: number }[],
  shots: XgPoint[],
  sampleSize: number,
): XgProfile {
  return {
    scope,
    target_id: targetId,
    label,
    team,
    total_xg: totalXg,
    actual_goals: actualGoals,
    finishing_delta: Number((actualGoals - totalXg).toFixed(3)),
    shots,
    zones,
    model_version: "snapshot-xg-view-v1",
    training_window: "statsbomb_open_data_plus_world_cup",
    sample_size: sampleSize,
  };
}

async function localTournamentCurrent(): Promise<TournamentCurrent> {
  const bundle = await loadDemoBundle();
  return buildTournamentCurrent(bundle.tournament);
}

async function localFixtures(): Promise<Fixture[]> {
  const bundle = await loadDemoBundle();
  return bundle.tournament.fixtures;
}

async function localStandings(): Promise<Standing[]> {
  const bundle = await loadDemoBundle();
  return buildStandings(bundle.tournament);
}

async function localTeams(): Promise<TeamProfile[]> {
  const bundle = await loadDemoBundle();
  return buildTeamProfiles(bundle.tournament);
}

async function localPlayers(): Promise<{ players: PlayerProfile[]; kickers: KickerProfile[]; keepers: KeeperProfile[] }> {
  return buildPlayerPayload(await loadDemoBundle());
}

async function localPredictMatch(payload: {
  home_team: string;
  away_team: string;
  neutral_site: boolean;
  stage: string;
}): Promise<MatchPrediction> {
  const bundle = await loadDemoBundle();
  const teamLookup = new Map(bundle.tournament.teams.map((team) => [team.name, team]));
  const home = teamLookup.get(payload.home_team);
  const away = teamLookup.get(payload.away_team);
  if (!home || !away) {
    throw new Error("Unknown team in match prediction request.");
  }

  const eloDiff = home.elo_rating - away.elo_rating;
  const formDiff = home.recent_form_points - away.recent_form_points;
  const hostFlag = Number(home.host || away.host);
  const homeScore = (0.65 * eloDiff) / 100 + 0.2 * formDiff + 0.1 * hostFlag;
  const awayScore = (-0.65 * eloDiff) / 100 - 0.2 * formDiff;
  const drawScore = 0.2 - Math.abs(eloDiff) / 450;
  const [homeWin, draw, awayWin] = roundProbabilities(...softmax([homeScore, drawScore, awayScore]) as [number, number, number]);

  return {
    home_win_probability: homeWin,
    draw_probability: draw,
    away_win_probability: awayWin,
    projected_winner: homeWin >= awayWin ? payload.home_team : payload.away_team,
    model_version: "heuristic-fallback-v1",
    training_window: "snapshot_priors",
    sample_size: 48,
    mode: "heuristic_fallback",
    top_drivers: [
      `Elo edge: ${eloDiff >= 0 ? payload.home_team : payload.away_team}`,
      `Recent form edge: ${formDiff >= 0 ? payload.home_team : payload.away_team}`,
      hostFlag ? "Host indicator applied" : "Neutral-site assumptions applied",
    ],
  };
}

async function localTeamXg(teamId: string): Promise<XgProfile> {
  const bundle = await loadDemoBundle();
  const team = bundle.xg.teams.find((entry) => entry.team_id === teamId);
  if (!team) {
    throw new Error(`Unknown xG team: ${teamId}`);
  }
  return buildXgProfile("team", teamId, team.label, team.label, team.total_xg, team.actual_goals, team.zones, team.shots, team.sample_size);
}

async function localPlayerXg(playerId: string): Promise<XgProfile> {
  const bundle = await loadDemoBundle();
  const player = bundle.xg.players.find((entry) => entry.player_id === playerId);
  if (!player) {
    throw new Error(`Unknown xG player: ${playerId}`);
  }
  return buildXgProfile(
    "player",
    playerId,
    player.player_name,
    player.team,
    player.total_xg,
    player.actual_goals,
    player.zones,
    player.shots,
    player.sample_size,
  );
}

async function localPredictPenalty(payload: {
  player_id: string;
  keeper_id: string;
  context: Record<string, unknown>;
}): Promise<PenaltyPrediction> {
  const bundle = await loadDemoBundle();
  const kicker = bundle.penalty.kickers.find((entry) => entry.player_id === payload.player_id);
  const keeper = bundle.penalty.keepers.find((entry) => entry.keeper_id === payload.keeper_id);
  if (!kicker || !keeper) {
    throw new Error("Unknown penalty profile requested.");
  }

  const pressure = Number(payload.context.pressure ?? 0.5);
  const keeperBias = keeper.save_bias[kicker.preferred_zone] ?? 0.2;
  const baseProbability = kicker.conversion_rate - keeper.save_rate * 0.35 - pressure * 0.08 - keeperBias * 0.05;
  const scoringProbability = Math.min(0.95, Math.max(0.45, baseProbability));

  return {
    player_id: payload.player_id,
    keeper_id: payload.keeper_id,
    scoring_probability: Number(scoringProbability.toFixed(4)),
    likely_target_zone: kicker.preferred_zone,
    target_zone_probabilities: kicker.target_zone_probabilities,
    model_version: "penalty-profile-v1",
    training_window: "major_tournaments_open_data",
    sample_size: kicker.sample_size,
    notes: [
      `${kicker.player_name} prefers ${kicker.preferred_zone}.`,
      `${keeper.keeper_name} save rate: ${keeper.save_rate.toFixed(2)}.`,
      "Pressure adjustment applied from request context.",
    ],
  };
}

function resolveTeamStrength(bundle: DemoBundle, teamName: string): number {
  const profile = bundle.tournament.teams.find((team) => team.name === teamName);
  if (!profile) {
    throw new Error(`Unknown team: ${teamName}`);
  }
  return profile.elo_rating + profile.recent_form_points * 20;
}

async function resolveSimulatedMatch(bundle: DemoBundle, rng: () => number, homeTeam: string, awayTeam: string): Promise<[string, string]> {
  const delta = resolveTeamStrength(bundle, homeTeam) - resolveTeamStrength(bundle, awayTeam);
  const noise = rng() * 160 - 80;
  const adjusted = delta + noise;

  if (Math.abs(adjusted) < 30) {
    const homeKicker = bundle.penalty.kickers[0];
    const awayKicker = bundle.penalty.kickers[bundle.penalty.kickers.length - 1];
    const homeKeeper = bundle.penalty.keepers[0];
    const awayKeeper = bundle.penalty.keepers[bundle.penalty.keepers.length - 1];

    const homePenalty = await localPredictPenalty({
      player_id: homeKicker.player_id,
      keeper_id: awayKeeper.keeper_id,
      context: { pressure: 0.85 },
    });
    const awayPenalty = await localPredictPenalty({
      player_id: awayKicker.player_id,
      keeper_id: homeKeeper.keeper_id,
      context: { pressure: 0.85 },
    });

    return homePenalty.scoring_probability >= awayPenalty.scoring_probability
      ? [homeTeam, "penalties"]
      : [awayTeam, "penalties"];
  }

  return adjusted >= 0 ? [homeTeam, "regulation"] : [awayTeam, "regulation"];
}

async function localSimulateTournament(seed = 2026): Promise<TournamentSimulation> {
  const bundle = await loadDemoBundle();
  const standings = buildStandings(bundle.tournament);
  const topTwo = Object.fromEntries(resolveTopTwo(standings, bundle.tournament.groups).map((team) => [team.slot, team.team]));
  const qualifiedThirdPlace = resolveBestThirdPlace(standings, bundle.tournament.groups);
  const thirdAssignments = resolveThirdPlaceSlots(qualifiedThirdPlace);
  const winners: Record<string, string> = {};
  const rng = createSeededRng(seed);

  const roundOf32: BracketMatch[] = [];
  for (const match of ROUND_OF_32_TEMPLATE) {
    const homeTeam = topTwo[match.home_slot] ?? match.home_slot;
    const awayTeam = match.away_slot.startsWith("3") ? thirdAssignments[match.match_id].team : (topTwo[match.away_slot] ?? match.away_slot);
    const [winner, resolution] = await resolveSimulatedMatch(bundle, rng, homeTeam, awayTeam);
    winners[`W${match.match_id}`] = winner;
    roundOf32.push({
      match_id: match.match_id,
      stage: match.stage,
      venue: match.venue,
      slot_home: match.home_slot,
      slot_away: match.away_slot,
      home_team: homeTeam,
      away_team: awayTeam,
      winner,
      resolution,
    });
  }

  const roundOf16: BracketMatch[] = [];
  const quarterfinals: BracketMatch[] = [];
  const semifinals: BracketMatch[] = [];

  for (const [stageName, collector] of [
    ["round_of_16", roundOf16],
    ["quarterfinal", quarterfinals],
    ["semifinal", semifinals],
  ] as const) {
    for (const match of NEXT_ROUNDS[stageName]) {
      const homeTeam = winners[match.home_slot];
      const awayTeam = winners[match.away_slot];
      const [winner, resolution] = await resolveSimulatedMatch(bundle, rng, homeTeam, awayTeam);
      winners[`W${match.match_id}`] = winner;
      collector.push({
        match_id: match.match_id,
        stage: stageName,
        venue: match.venue,
        slot_home: match.home_slot,
        slot_away: match.away_slot,
        home_team: homeTeam,
        away_team: awayTeam,
        winner,
        resolution,
      });
    }
  }

  const finalDefinition = NEXT_ROUNDS.final[0];
  const finalHome = winners[finalDefinition.home_slot];
  const finalAway = winners[finalDefinition.away_slot];
  const [champion, finalResolution] = await resolveSimulatedMatch(bundle, rng, finalHome, finalAway);

  return {
    qualified_third_place: qualifiedThirdPlace.map((team) => team.team),
    round_of_32: roundOf32,
    round_of_16: roundOf16,
    quarterfinals,
    semifinals,
    final: {
      match_id: finalDefinition.match_id,
      stage: "final",
      venue: finalDefinition.venue,
      slot_home: finalDefinition.home_slot,
      slot_away: finalDefinition.away_slot,
      home_team: finalHome,
      away_team: finalAway,
      winner: champion,
      resolution: finalResolution,
    },
    champion,
  };
}

export const api = {
  getTournamentCurrent: () =>
    withDemoFallback(() => request<TournamentCurrent>("/api/tournament/current"), localTournamentCurrent),
  getFixtures: () =>
    withDemoFallback(
      async () => (await request<{ fixtures: Fixture[] }>("/api/fixtures")).fixtures,
      localFixtures,
    ),
  getStandings: () => withDemoFallback(() => request<Standing[]>("/api/standings"), localStandings),
  getTeams: () =>
    withDemoFallback(
      async () => (await request<{ teams: TeamProfile[] }>("/api/teams")).teams,
      localTeams,
    ),
  getPlayers: () =>
    withDemoFallback(
      async () => {
        const payload = await request<{
          players: PlayerProfile[];
          kickers?: KickerProfile[];
          keepers: KeeperProfile[];
        }>("/api/players");
        return {
          players: payload.players,
          kickers: payload.kickers ?? payload.players.map(({ player_id, player_name }) => ({ player_id, player_name })),
          keepers: payload.keepers,
        };
      },
      localPlayers,
    ),
  predictMatch: (payload: { home_team: string; away_team: string; neutral_site: boolean; stage: string }) =>
    withDemoFallback(
      () => request<MatchPrediction>("/api/predict/match", { method: "POST", body: JSON.stringify(payload) }),
      () => localPredictMatch(payload),
    ),
  getTeamXg: (teamId: string) =>
    withDemoFallback(() => request<XgProfile>(`/api/xg/team/${teamId}`), () => localTeamXg(teamId)),
  getPlayerXg: (playerId: string) =>
    withDemoFallback(() => request<XgProfile>(`/api/xg/player/${playerId}`), () => localPlayerXg(playerId)),
  predictPenalty: (payload: { player_id: string; keeper_id: string; context: Record<string, unknown> }) =>
    withDemoFallback(
      () => request<PenaltyPrediction>("/api/predict/penalty", { method: "POST", body: JSON.stringify(payload) }),
      () => localPredictPenalty(payload),
    ),
  simulateTournament: (seed = 2026) =>
    withDemoFallback(
      () => request<TournamentSimulation>("/api/simulate/tournament", { method: "POST", body: JSON.stringify({ seed }) }),
      () => localSimulateTournament(seed),
    ),
};
