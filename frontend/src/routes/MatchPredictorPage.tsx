import { FormEvent, useEffect, useState } from "react";
import { api, type MatchPrediction, type TeamProfile } from "../lib/api";
import { ProbabilityBars } from "../components/ProbabilityBars";

export function MatchPredictorPage() {
  const [teams, setTeams] = useState<TeamProfile[]>([]);
  const [homeTeam, setHomeTeam] = useState("Mexico");
  const [awayTeam, setAwayTeam] = useState("South Africa");
  const [prediction, setPrediction] = useState<MatchPrediction | null>(null);

  useEffect(() => {
    void api.getTeams().then(setTeams);
  }, []);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const result = await api.predictMatch({
      home_team: homeTeam,
      away_team: awayTeam,
      neutral_site: false,
      stage: "group",
    });
    setPrediction(result);
  };

  return (
    <div className="page-grid two-column">
      <section className="panel">
        <p className="eyebrow">Match Predictor</p>
        <h2>Model the winner before kickoff</h2>
        <form className="stack-form" onSubmit={handleSubmit}>
          <label>
            Home team
            <select value={homeTeam} onChange={(event) => setHomeTeam(event.target.value)}>
              {teams.map((team) => <option key={team.team_id} value={team.name}>{team.name}</option>)}
            </select>
          </label>
          <label>
            Away team
            <select value={awayTeam} onChange={(event) => setAwayTeam(event.target.value)}>
              {teams.map((team) => <option key={team.team_id} value={team.name}>{team.name}</option>)}
            </select>
          </label>
          <button className="accent-button" type="submit">Run prediction</button>
        </form>
      </section>

      <section className="panel">
        {prediction ? (
          <>
            <div className="section-header">
              <h2>{prediction.projected_winner} edge</h2>
              <small>{prediction.model_version} • {prediction.mode}</small>
            </div>
            <ProbabilityBars
              homeLabel={homeTeam}
              awayLabel={awayTeam}
              home={prediction.home_win_probability}
              draw={prediction.draw_probability}
              away={prediction.away_win_probability}
            />
            <ul className="detail-list">
              {prediction.top_drivers.map((driver) => <li key={driver}>{driver}</li>)}
            </ul>
          </>
        ) : (
          <div className="empty-card">Choose a matchup to generate probabilities and driver explanations.</div>
        )}
      </section>
    </div>
  );
}

