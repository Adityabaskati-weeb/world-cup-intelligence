import type { BracketMatch, TournamentSimulation } from "../lib/api";

type Props = {
  simulation: TournamentSimulation | null;
};

function RoundColumn({ title, matches }: { title: string; matches: BracketMatch[] }) {
  return (
    <section className="bracket-column">
      <h4>{title}</h4>
      {matches.map((match) => (
        <article key={match.match_id} className="bracket-match">
          <div className="match-meta">
            <span>M{match.match_id}</span>
            <span>{match.venue}</span>
          </div>
          <strong>{match.home_team} vs {match.away_team}</strong>
          <small>{match.winner} via {match.resolution}</small>
        </article>
      ))}
    </section>
  );
}

export function BracketView({ simulation }: Props) {
  if (!simulation) {
    return <div className="empty-card">Run the tournament simulator to render the knockout path.</div>;
  }

  return (
    <div className="bracket-grid">
      <RoundColumn title="Round of 32" matches={simulation.round_of_32.slice(0, 4)} />
      <RoundColumn title="Round of 16" matches={simulation.round_of_16.slice(0, 4)} />
      <RoundColumn title="Quarterfinals" matches={simulation.quarterfinals} />
      <RoundColumn title="Semifinals" matches={simulation.semifinals} />
      <section className="bracket-column">
        <h4>Final</h4>
        <article className="bracket-match final-card">
          <div className="match-meta">
            <span>M{simulation.final.match_id}</span>
            <span>{simulation.final.venue}</span>
          </div>
          <strong>{simulation.final.home_team} vs {simulation.final.away_team}</strong>
          <small>Champion: {simulation.champion}</small>
        </article>
      </section>
    </div>
  );
}

