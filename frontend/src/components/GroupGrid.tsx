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
              <div>
                <p className="group-kicker">Group {group}</p>
                <h3>Projected table</h3>
              </div>
              <span className="group-cap">{teams.length} teams</span>
            </div>
            <div className="group-table-head">
              <span>Team</span>
              <span>Pts</span>
              <span>GD</span>
            </div>
            <ul className="team-list team-list-compact">
              {table.length
                ? table.map((row) => (
                    <li key={row.team} className={`table-row rank-${row.rank <= 2 ? "qualifying" : row.rank === 3 ? "playoff" : "elimination"}`}>
                      <div className="team-line team-line-table">
                        <strong>
                          <span className="team-rank">{row.rank}</span>
                          {row.team}
                        </strong>
                        <span>{row.points}</span>
                        <span>{row.goal_difference >= 0 ? `+${row.goal_difference}` : row.goal_difference}</span>
                      </div>
                      <small className="team-subline">
                        {row.goals_for}:{row.goals_against} goals | {row.won}-{row.drawn}-{row.lost} record
                      </small>
                    </li>
                  ))
                : teams.map((team) => (
                    <li key={team} className="table-row">
                      <strong>{team}</strong>
                    </li>
                  ))}
            </ul>
            <p className="group-footnote">Top two advance automatically. Strong third-place records stay alive.</p>
          </section>
        );
      })}
    </div>
  );
}
