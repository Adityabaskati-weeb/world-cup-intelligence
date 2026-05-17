import { Link } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import { RefreshStatusStrip } from "../components/RefreshStatusStrip";
import { StatusMessage } from "../components/StatusMessage";
import { api, describeError, type Fixture, type RefreshStatus, type TournamentCurrent } from "../lib/api";

const sceneImages = {
  hero:
    "https://images.pexels.com/photos/30552971/pexels-photo-30552971.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260",
  anticipation:
    "https://images.pexels.com/photos/12469622/pexels-photo-12469622.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260",
  knockout:
    "https://images.pexels.com/photos/1387037/pexels-photo-1387037.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260",
  analysis:
    "https://images.pexels.com/photos/4902691/pexels-photo-4902691.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260",
  penalty:
    "https://images.pexels.com/photos/30726646/pexels-photo-30726646.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260",
} as const;

const storyScenes = [
  {
    label: "Tunnel hush",
    title: "Before the first whistle, the tournament already has a pulse.",
    copy:
      "Stadium lights, crowd pressure, and host-city energy set the emotional context. The platform begins there instead of skipping straight to widgets.",
    note: "Crowd atmosphere, opening tension, and host-city charge.",
    image: sceneImages.anticipation,
  },
  {
    label: "Knockout swing",
    title: "Knockout football turns every chance into memory or regret.",
    copy:
      "One finish, one save, one penalty order decision can redirect a whole bracket. The product is built to read those pressure swings clearly.",
    note: "Pressure-state reading for moments that decide a whole month.",
    image: sceneImages.knockout,
  },
  {
    label: "Pattern recognition",
    title: "Then the hidden layer appears: probability, shot quality, and duel tendencies.",
    copy:
      "Match forecasting, xG storytelling, and penalty scouting sit behind the emotion without draining it out of the sport.",
    note: "Real match footage meets tactical overlays and field geometry.",
    image: sceneImages.analysis,
  },
] as const;

const moduleHighlights = [
  {
    kicker: "Tournament pulse",
    title: "Tournament Pulse",
    copy:
      "Track group races, fixtures, and the 48-team bracket through a cleaner football-first reading of the 2026 format.",
    to: "/tournament-hub",
  },
  {
    kicker: "Forecasting",
    title: "Match Center",
    copy:
      "Read likely winners through team strength, recent form, home-host context, and pressure-state framing instead of generic model output.",
    to: "/match-center",
  },
  {
    kicker: "Shot craft",
    title: "xG Explorer",
    copy:
      "Move from team shot territory to individual finishing patterns, then understand where the best chances are actually forming.",
    to: "/xg-explorer",
  },
  {
    kicker: "Pressure duel",
    title: "Penalty Lab",
    copy:
      "Turn a shootout into a scouted duel between taker and keeper, with placement tendencies and conversion context baked in.",
    to: "/penalty-lab",
  },
] as const;

export function LandingPage() {
  const [tournament, setTournament] = useState<TournamentCurrent | null>(null);
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [refreshStatus, setRefreshStatus] = useState<RefreshStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);
      setRefreshError(null);
      const [tournamentResult, fixturesResult, refreshResult] = await Promise.allSettled([
        api.getTournamentCurrent(),
        api.getFixtures(),
        api.getRefreshStatus(),
      ]);

      if (cancelled) {
        return;
      }

      let nextError: string | null = null;
      if (tournamentResult.status === "fulfilled") {
        setTournament(tournamentResult.value);
      } else {
        nextError = describeError(tournamentResult.reason);
      }

      if (fixturesResult.status === "fulfilled") {
        setFixtures(fixturesResult.value);
      } else if (!nextError) {
        nextError = describeError(fixturesResult.reason);
      }

      if (refreshResult.status === "fulfilled") {
        setRefreshStatus(refreshResult.value);
      } else {
        setRefreshStatus(null);
        setRefreshError(describeError(refreshResult.reason));
      }

      setError(nextError);
      setLoading(false);
    };

    void load();
    return () => {
      cancelled = true;
    };
  }, [reloadKey]);

  const openingFixture = fixtures[0];
  const statTape = useMemo(
    () => [
      {
        label: "Tournament window",
        value: tournament ? `${tournament.start_date} to ${tournament.end_date}` : "June 11 to July 19, 2026",
      },
      {
        label: "Format",
        value: tournament
          ? `${tournament.format.group_count} groups, ${tournament.format.teams_per_group} teams each`
          : "12 groups, 4 teams each",
      },
      {
        label: "Hosts",
        value: tournament ? tournament.host_countries.join(" / ") : "Canada / Mexico / USA",
      },
      {
        label: "Opening night",
        value: openingFixture ? `${openingFixture.home_team} vs ${openingFixture.away_team}` : "Opening fixture loading",
      },
    ],
    [openingFixture, tournament],
  );

  return (
    <div className="landing-page">
      <section className="landing-hero" style={{ ["--scene-image" as string]: `url(${sceneImages.hero})` }}>
        <div className="landing-scrim" />
        <div className="landing-grid">
          <div className="landing-copy">
            <p className="eyebrow">Football intelligence for World Cup 2026</p>
            <h1>Feel the tournament first. Then read the hidden game.</h1>
            <p className="landing-lead">
              Matchflow is a cinematic football reasoning platform for the men&apos;s FIFA World Cup 2026. It moves
              from floodlights and matchday tension into explainable forecasts, chance quality, and knockout pressure
              without flattening the sport into raw percentages.
            </p>
            <div className="landing-action-row">
              <Link className="accent-button" to="/tournament-hub">
                Enter tournament pulse
              </Link>
              <Link className="ghost-button ghost-button-light" to="/match-center">
                Open match center
              </Link>
            </div>
          </div>

          <aside className="landing-side-rail">
            <div className="landing-side-card">
              <span className="landing-side-label">Matchday pulse</span>
              <strong>{openingFixture ? `${openingFixture.home_team} vs ${openingFixture.away_team}` : "Loading opening fixture"}</strong>
              <p>{openingFixture ? `${openingFixture.venue} | ${openingFixture.date}` : "The first night of the tournament sets the emotional tone."}</p>
            </div>
            <div className="landing-side-card landing-side-card-muted">
              <span className="landing-side-label">Why it lands</span>
              <strong>Emotion, reasoning, and tournament pulse</strong>
              <p>
                Instead of dropping a generic win probability, Matchflow shows why the edge exists, where pressure
                lives, and how tournament context changes the read.
              </p>
            </div>
          </aside>
        </div>

        <div className="landing-stat-tape" aria-label="Tournament summary">
          {statTape.map((item) => (
            <article key={item.label} className="landing-stat-chip">
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </article>
          ))}
        </div>
      </section>

      <section className="panel landing-signal-panel">
        <div className="landing-section-head">
          <p className="eyebrow">Tournament pulse</p>
          <h2>The platform keeps the signal layer readable, honest, and close to the football story.</h2>
          <p>
            Live fixture sync, tournament reference snapshots, xG intelligence, and penalty scouting each show their
            own readiness state so users can trust what they are seeing.
          </p>
        </div>
        {refreshStatus ? (
          <RefreshStatusStrip
            status={refreshStatus}
            title="Signal readiness"
            subtitle="Each model surface carries its own sync state, timestamp, and source context."
          />
        ) : refreshError ? (
          <StatusMessage title="Tournament pulse is temporarily unavailable." tone="info">
            {refreshError}
          </StatusMessage>
        ) : null}
      </section>

      {error ? (
        <div className="section-stack">
          <StatusMessage title="Live tournament context is temporarily unavailable." tone="info">
            {error}
          </StatusMessage>
          <button className="ghost-button" type="button" onClick={() => setReloadKey((value) => value + 1)}>
            Retry landing data
          </button>
        </div>
      ) : null}

      <section className="landing-story-rail">
        {storyScenes.map((scene, index) => (
          <article
            key={scene.title}
            className={`landing-scene landing-scene-${index + 1}`}
            style={{ ["--scene-image" as string]: `url(${scene.image})` }}
          >
            <div className="landing-scrim landing-scrim-soft" />
            <div className="landing-scene-layout">
              <div className="landing-scene-copy">
                <p className="eyebrow">{scene.label}</p>
                <h2>{scene.title}</h2>
                <p>{scene.copy}</p>
              </div>
              <aside className="landing-scene-note">
                <span className="landing-side-label">Scene note</span>
                <p>{scene.note}</p>
              </aside>
            </div>
          </article>
        ))}
      </section>

      <section className="landing-transition-panel">
        <div className="landing-transition-copy">
          <p className="eyebrow">From atmosphere to analysis</p>
          <h2>The product reveals itself only after the tournament story is set.</h2>
          <p>
            Instead of dumping users into admin cards, the platform opens with football tension and then hands them
            into focused decision surfaces built for scouting, forecasting, and tournament reading. The differentiator
            is not one model output, but a full reasoning layer around match momentum, shot quality, and shootout
            pressure.
          </p>
        </div>
      </section>

      <section className="landing-module-section">
        <div className="landing-section-head">
          <p className="eyebrow">Platform surfaces</p>
          <h2>Four connected lenses. One tournament story.</h2>
        </div>
        <div className="landing-module-grid">
          {moduleHighlights.map((module) => (
            <article key={module.title} className="landing-module-card">
              <p className="landing-module-kicker">{module.kicker}</p>
              <h3>{module.title}</h3>
              <p>{module.copy}</p>
              <Link to={module.to} className="landing-text-link">
                Open {module.title}
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-closing-cta" style={{ ["--scene-image" as string]: `url(${sceneImages.penalty})` }}>
        <div className="landing-scrim" />
        <div className="landing-closing-copy">
          <p className="eyebrow">Ready for the full tournament view?</p>
          <h2>Step from the atmosphere into the working intelligence layer.</h2>
          <p>
            Explore the group races, simulate the bracket, study chance quality, and compare penalty duels without
            losing the feeling of the competition itself.
          </p>
          <div className="landing-action-row">
            <Link className="accent-button" to="/tournament-hub">
              Open tournament pulse
            </Link>
            <Link className="ghost-button ghost-button-light" to="/penalty-lab">
              Jump to penalty lab
            </Link>
          </div>
        </div>
      </section>

      {loading ? (
        <StatusMessage title="Shaping the live tournament context..." tone="loading">
          Pulling fixtures and tournament framing into the landing experience.
        </StatusMessage>
      ) : null}
    </div>
  );
}
