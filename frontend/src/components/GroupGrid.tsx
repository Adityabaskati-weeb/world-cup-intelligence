import type { Standing, TournamentCurrent } from "../lib/api";

type Props = {
  tournament: TournamentCurrent | null;
  standings: Standing[];
};

export function GroupGrid({ tournament, standings }: Props) {
  if (!tournament) {
    return <div className="empty-card">Loading groups...</div>;
  }

  return (
    <div className="group-grid">
      {Object.entries(tournament.groups).map(([group, teams]) => {
        const table = standings.filter((row) => row.group === group);
        return (
          <section key={group} className="group-card">
            <div className="group-card-header">
              <h3>Group {group}</h3>
              <span>{teams.length} teams</span>
            </div>
            <ul className="team-list">
              {table.length
                ? table.map((row) => (
                    <li key={row.team}>
                      <strong>{row.rank}. {row.team}</strong>
                      <span>{row.points} pts</span>
                    </li>
                  ))
                : teams.map((team) => (
                    <li key={team}>
                      <strong>{team}</strong>
                    </li>
                  ))}
            </ul>
          </section>
        );
      })}
    </div>
  );
}

