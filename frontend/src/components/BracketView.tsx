import type { BracketMatch, TournamentSimulation } from "../lib/api";
import { StatusMessage } from "./StatusMessage";

type Props = {
  simulation: TournamentSimulation | null;
};

function RoundColumn({ title, matches }: { title: string; matches: BracketMatch[] }) {
  return (
    <section className="bracket-column">
      <div className="bracket-column-header">
        <h4>{title}</h4>
        <span>{matches.length} ties</span>
      </div>
      {matches.map((match) => (
        <article key={match.match_id} className="bracket-match">
          <div className="match-meta">
            <span>M{match.match_id}</span>
            <span>{match.venue}</span>
          </div>
          <strong>{match.home_team} vs {match.away_team}</strong>
          <small>
            Winner <strong>{match.winner}</strong> via {match.resolution}
          </small>
        </article>
      ))}
    </section>
  );
}

export function BracketView({ simulation }: Props) {
  if (!simulation) {
    return (
      <StatusMessage title="Run the tournament simulator to render the knockout path." tone="info">
        The full round-of-32 through final bracket will appear here.
      </StatusMessage>
    );
  }

  return (
    <div className="bracket-grid">
      <RoundColumn title="Round of 32" matches={simulation.round_of_32} />
      <RoundColumn title="Round of 16" matches={simulation.round_of_16} />
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
          <small>
            Champion: {simulation.champion} | via {simulation.final.resolution}
          </small>
        </article>
      </section>
    </div>
  );
}
