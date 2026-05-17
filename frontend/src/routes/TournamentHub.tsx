import { useEffect, useMemo, useState } from "react";
import { BracketView } from "../components/BracketView";
import { GroupGrid } from "../components/GroupGrid";
import { MetricCards } from "../components/MetricCards";
import { RefreshStatusStrip } from "../components/RefreshStatusStrip";
import { StatusMessage } from "../components/StatusMessage";
import {
  api,
  describeError,
  type Fixture,
  type RefreshStatus,
  type RuntimeMode,
  type Standing,
  type TournamentCurrent,
  type TournamentSimulation,
} from "../lib/api";

function formatStageLabel(fixture: Fixture) {
  return fixture.group ? `Group ${fixture.group}` : fixture.stage.replaceAll("_", " ");
}

export function TournamentHub() {
  const [tournament, setTournament] = useState<TournamentCurrent | null>(null);
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [standings, setStandings] = useState<Standing[]>([]);
  const [simulation, setSimulation] = useState<TournamentSimulation | null>(null);
  const [refreshStatus, setRefreshStatus] = useState<RefreshStatus | null>(null);
  const [runtimeMode, setRuntimeMode] = useState<RuntimeMode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fixturesError, setFixturesError] = useState<string | null>(null);
  const [standingsError, setStandingsError] = useState<string | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [simulationLoading, setSimulationLoading] = useState(false);
  const [simulationError, setSimulationError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);
      setFixturesError(null);
      setStandingsError(null);
      setHealthError(null);
      setRefreshError(null);

      const [healthResult, tournamentResult, fixturesResult, standingsResult, refreshResult] = await Promise.allSettled([
        api.getHealth(),
        api.getTournamentCurrent(),
        api.getFixtures(),
        api.getStandings(),
        api.getRefreshStatus(),
      ]);

      if (cancelled) {
        return;
      }

      if (healthResult.status === "fulfilled") {
        setRuntimeMode(healthResult.value.runtime_mode);
      } else {
        setRuntimeMode(null);
        setHealthError(describeError(healthResult.reason));
      }

      if (tournamentResult.status === "fulfilled") {
        setTournament(tournamentResult.value);
      } else {
        setTournament(null);
        setError(describeError(tournamentResult.reason));
      }

      if (fixturesResult.status === "fulfilled") {
        setFixtures(fixturesResult.value);
      } else {
        setFixtures([]);
        setFixturesError(describeError(fixturesResult.reason));
      }

      if (standingsResult.status === "fulfilled") {
        setStandings(standingsResult.value);
      } else {
        setStandings([]);
        setStandingsError(describeError(standingsResult.reason));
      }

      if (refreshResult.status === "fulfilled") {
        setRefreshStatus(refreshResult.value);
      } else {
        setRefreshStatus(null);
        setRefreshError(describeError(refreshResult.reason));
      }

      setLoading(false);
    };

    void load();
    return () => {
      cancelled = true;
    };
  }, [reloadKey]);

  const featuredFixtures = fixtures.slice(0, 6);
  const openingFixture = featuredFixtures[0];
  const projectedLeaders = standings.filter((row) => row.rank === 1);

  const tournamentStats = useMemo(
    () => [
      {
        label: "Data feed",
        value:
          runtimeMode === "live_api"
            ? "Live API"
            : runtimeMode === "snapshot_backed_api"
              ? "Snapshot-backed API"
              : "API status unavailable",
        hint:
          runtimeMode === "live_api"
            ? "FastAPI is serving the active production response layer."
            : runtimeMode === "snapshot_backed_api"
              ? "The backend is serving tournament snapshots through the real API contract."
              : healthError ?? "The health endpoint did not answer, so runtime status could not be confirmed.",
      },
      {
        label: "Hosts",
        value: tournament ? tournament.host_countries.join(" / ") : "Canada / Mexico / USA",
        hint: "Co-host logic is baked into the tournament config.",
      },
      {
        label: "Format",
        value: tournament ? `${tournament.format.group_count} groups / ${tournament.format.teams_per_group} teams` : "12 groups / 4 teams",
        hint: "Best-third-place advancement is supported in the simulator.",
      },
      {
        label: "Opening fixture",
        value: openingFixture ? `${openingFixture.home_team} vs ${openingFixture.away_team}` : "Fixture feed pending",
        hint: openingFixture ? `${openingFixture.venue} on ${openingFixture.date}` : "The first night of the tournament sets the tone.",
      },
    ],
    [healthError, openingFixture, runtimeMode, tournament],
  );

  const storylineCards = useMemo(
    () => [
      {
        label: "Group races",
        value: `${Object.keys(tournament?.groups ?? {}).length || 12} tables`,
        hint: "Top two sides advance automatically from each group.",
      },
      {
        label: "Projected leaders",
        value: `${projectedLeaders.length}`,
        hint: "Teams currently topping their groups in the active standings feed.",
      },
      {
        label: "Host cities",
        value: `${tournament?.host_cities.length ?? 16}`,
        hint: "The tournament footprint spans North America.",
      },
    ],
    [projectedLeaders.length, tournament],
  );

  const watchList = useMemo(() => {
    if (!tournament) {
      return [];
    }

    const stories = [
      `${Object.keys(tournament.groups).length} groups feed the 2026 bracket, with eight third-place sides surviving the first cut.`,
      `${projectedLeaders.length || 0} current group leaders are surfaced from the standings feed.`,
      "The knockout simulator uses the same 48-team rules that shape the tournament hub.",
    ];

    if (openingFixture) {
      stories.unshift(`Opening night starts with ${openingFixture.home_team} against ${openingFixture.away_team} in ${openingFixture.venue}.`);
    }

    if (fixturesError) {
      stories.push("Fixture sync is temporarily unavailable, so upcoming-match framing is limited to the broader tournament picture.");
    }

    return stories;
  }, [fixturesError, openingFixture, projectedLeaders.length, tournament]);

  const handleSimulation = async () => {
    setSimulationLoading(true);
    setSimulationError(null);
    try {
      setSimulation(await api.simulateTournament());
    } catch (nextError) {
      setSimulationError(describeError(nextError));
    } finally {
      setSimulationLoading(false);
    }
  };

  return (
    <div className="page-grid">
      <section className="hero-panel hero-panel-large">
        <div className="hero-header">
          <div>
            <p className="eyebrow">Tournament Pulse</p>
            <h1>{tournament?.name ?? "Loading tournament hub..."}</h1>
          </div>
          <span className={`status-pill ${runtimeMode === "live_api" ? "live" : "demo"}`}>
            {runtimeMode === "live_api"
              ? "Live API"
              : runtimeMode === "snapshot_backed_api"
                ? "Snapshot-backed API"
                : "API status unavailable"}
          </span>
        </div>
        <p className="hero-copy">
          Move from the tournament atmosphere into the working match layer: qualification lines, opening fixtures,
          projected group leaders, sync-state awareness, and the knockout path that turns pressure into story.
        </p>
        <MetricCards items={tournamentStats} />
      </section>

      {refreshStatus ? (
        <RefreshStatusStrip
          status={refreshStatus}
          title="Tournament pulse"
          subtitle="See which tournament reads are live, which are reference-backed, and where the signal is starting to age."
        />
      ) : refreshError ? (
        <StatusMessage title="Sync-state panel is unavailable." tone="info">
          {refreshError}
        </StatusMessage>
      ) : null}

      {error ? (
        <div className="section-stack">
          <StatusMessage title="Tournament data could not be loaded." tone="error">
            {error}
          </StatusMessage>
          <button className="ghost-button" type="button" onClick={() => setReloadKey((value) => value + 1)}>
            Retry hub load
          </button>
        </div>
      ) : null}

      <div className="page-grid two-column page-section-grid">
        <section className="panel">
          <div className="section-header">
            <div>
              <h2>Group races and standings</h2>
              <small>Read the tables the way an analyst would: qualification line first, noise second.</small>
            </div>
          </div>
          <MetricCards items={storylineCards} compact />
          {loading ? (
            <StatusMessage title="Loading tournament tables..." tone="loading">
              Pulling groups, fixtures, and standings into the hub.
            </StatusMessage>
          ) : standingsError ? (
            <div className="section-stack">
              <StatusMessage title="Standings feed is unavailable." tone="error">
                {standingsError}
              </StatusMessage>
              <button className="ghost-button" type="button" onClick={() => setReloadKey((value) => value + 1)}>
                Retry tables
              </button>
            </div>
          ) : (
            <GroupGrid tournament={tournament} standings={standings} />
          )}
        </section>

        <section className="panel">
          <div className="section-header">
            <div>
              <h2>Tournament watchlist</h2>
              <small>The storylines worth understanding before you jump into the models.</small>
            </div>
          </div>
          <div className="story-stack">
            {watchList.length ? (
              watchList.map((story) => (
                <article key={story} className="story-card">
                  <p>{story}</p>
                </article>
              ))
            ) : (
              <StatusMessage title="Storylines will appear once tournament context is loaded." tone="info">
                Reload the hub after the API is available to restore fixture and standings framing.
              </StatusMessage>
            )}
          </div>
        </section>
      </div>

      <section className="panel">
        <div className="section-header">
          <div>
            <h2>Upcoming fixtures</h2>
            <small>Opening matchdays, venue context, and the first knockout slots.</small>
          </div>
          <span className="section-badge">{featuredFixtures.length} highlighted</span>
        </div>
        {fixturesError ? (
          <div className="section-stack">
            <StatusMessage title="Fixtures could not be loaded." tone="error">
              {fixturesError}
            </StatusMessage>
            <button className="ghost-button" type="button" onClick={() => setReloadKey((value) => value + 1)}>
              Retry fixtures
            </button>
          </div>
        ) : featuredFixtures.length ? (
          <div className="fixture-list fixture-timeline">
            {featuredFixtures.map((fixture) => (
              <article key={fixture.match_id} className="fixture-card fixture-card-timeline">
                <div className="fixture-kicker">
                  <span>{formatStageLabel(fixture)}</span>
                  <span>
                    {fixture.date} | {fixture.kickoff_local}
                  </span>
                </div>
                <strong>
                  {fixture.home_team} vs {fixture.away_team}
                </strong>
                <small>
                  {fixture.venue} | {fixture.status}
                </small>
              </article>
            ))}
          </div>
        ) : (
          <StatusMessage title="No fixtures are available yet." tone="info">
            The fixture feed is connected, but there are no scheduled rows to highlight for this state.
          </StatusMessage>
        )}
      </section>

      <section className="panel panel-wide">
        <div className="section-header">
          <div>
            <h2>Knockout simulator</h2>
            <small>Resolve the bracket under the 2026 format and see where penalties start deciding the path.</small>
          </div>
          <button className="accent-button" onClick={() => void handleSimulation()} disabled={simulationLoading || !tournament}>
            {simulationLoading ? "Simulating..." : "Simulate bracket"}
          </button>
        </div>
        {simulationError ? (
          <StatusMessage title="Simulation failed." tone="error">
            {simulationError}
          </StatusMessage>
        ) : null}
        <BracketView simulation={simulation} />
      </section>
    </div>
  );
}
