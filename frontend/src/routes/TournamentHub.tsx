import { useEffect, useState } from "react";
import { BracketView } from "../components/BracketView";
import { GroupGrid } from "../components/GroupGrid";
import { api, type Fixture, type Standing, type TournamentCurrent, type TournamentSimulation } from "../lib/api";

export function TournamentHub() {
  const [tournament, setTournament] = useState<TournamentCurrent | null>(null);
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [standings, setStandings] = useState<Standing[]>([]);
  const [simulation, setSimulation] = useState<TournamentSimulation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void Promise.all([api.getTournamentCurrent(), api.getFixtures(), api.getStandings()]).then(
      ([current, nextFixtures, nextStandings]) => {
        setTournament(current);
        setFixtures(nextFixtures);
        setStandings(nextStandings);
        setLoading(false);
      },
    );
  }, []);

  return (
    <div className="page-grid">
      <section className="hero-panel">
        <p className="eyebrow">World Cup Intelligence 2026</p>
        <h1>{tournament?.name ?? "Loading 2026 tournament hub..."}</h1>
        <p className="hero-copy">
          Built for the June 11, 2026 to July 19, 2026 tournament window, with config-driven refreshes for qualifiers,
          future draws, and the next World Cup cycle.
        </p>
        <p className="hero-copy">Runs against the live API when available and falls back to the bundled 2026 demo snapshot when it is not.</p>
        <div className="hero-stats">
          <div><span>Hosts</span><strong>{tournament?.host_countries.join(" / ")}</strong></div>
          <div><span>Format</span><strong>48 teams / 12 groups / Round of 32</strong></div>
          <div><span>Update cadence</span><strong>Yearly backfill + tournament sync</strong></div>
        </div>
      </section>

      <section className="panel">
        <div className="section-header">
          <h2>Groups</h2>
          <small>Projected standings are seeded from the local snapshot.</small>
        </div>
        {loading ? <div className="empty-card">Loading tournament data...</div> : <GroupGrid tournament={tournament} standings={standings} />}
      </section>

      <section className="panel">
        <div className="section-header">
          <h2>Upcoming fixtures</h2>
          <small>Opening matchdays plus bracket slots.</small>
        </div>
        <div className="fixture-list">
          {fixtures.slice(0, 10).map((fixture) => (
            <article key={fixture.match_id} className="fixture-card">
              <div className="match-meta">
                <span>{fixture.group ? `Group ${fixture.group}` : fixture.stage.replaceAll("_", " ")}</span>
                <span>{fixture.date} / {fixture.kickoff_local}</span>
              </div>
              <strong>{fixture.home_team} vs {fixture.away_team}</strong>
              <small>{fixture.venue}</small>
            </article>
          ))}
        </div>
      </section>

      <section className="panel panel-wide">
        <div className="section-header">
          <h2>Knockout simulator</h2>
          <button className="accent-button" onClick={() => void api.simulateTournament().then(setSimulation)}>
            Simulate bracket
          </button>
        </div>
        <BracketView simulation={simulation} />
      </section>
    </div>
  );
}
