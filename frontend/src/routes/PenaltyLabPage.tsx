import { FormEvent, useEffect, useState } from "react";
import { api, type KeeperProfile, type PenaltyPrediction, type PlayerProfile } from "../lib/api";

export function PenaltyLabPage() {
  const [players, setPlayers] = useState<PlayerProfile[]>([]);
  const [keepers, setKeepers] = useState<KeeperProfile[]>([]);
  const [playerId, setPlayerId] = useState("harry-kane");
  const [keeperId, setKeeperId] = useState("emiliano-martinez");
  const [prediction, setPrediction] = useState<PenaltyPrediction | null>(null);

  useEffect(() => {
    void api.getPlayers().then((payload) => {
      setPlayers(payload.players);
      setKeepers(payload.keepers);
    });
  }, []);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const result = await api.predictPenalty({
      player_id: playerId,
      keeper_id: keeperId,
      context: { pressure: 0.85, tournament_stage: "knockout" },
    });
    setPrediction(result);
  };

  return (
    <div className="page-grid two-column">
      <section className="panel">
        <p className="eyebrow">Penalty Lab</p>
        <h2>Score odds, dive tendencies, target zones</h2>
        <form className="stack-form" onSubmit={handleSubmit}>
          <label>
            Kicker
            <select value={playerId} onChange={(event) => setPlayerId(event.target.value)}>
              {players.map((player) => <option key={player.player_id} value={player.player_id}>{player.player_name}</option>)}
            </select>
          </label>
          <label>
            Keeper
            <select value={keeperId} onChange={(event) => setKeeperId(event.target.value)}>
              {keepers.map((keeper) => <option key={keeper.keeper_id} value={keeper.keeper_id}>{keeper.keeper_name}</option>)}
            </select>
          </label>
          <button className="accent-button" type="submit">Compare matchup</button>
        </form>
      </section>

      <section className="panel">
        {prediction ? (
          <>
            <div className="section-header">
              <h2>{(prediction.scoring_probability * 100).toFixed(1)}% conversion</h2>
              <small>{prediction.model_version}</small>
            </div>
            <div className="hero-stats compact">
              <div><span>Likely zone</span><strong>{prediction.likely_target_zone}</strong></div>
              <div><span>Samples</span><strong>{prediction.sample_size}</strong></div>
              <div><span>Window</span><strong>{prediction.training_window}</strong></div>
            </div>
            <ul className="detail-list">
              {Object.entries(prediction.target_zone_probabilities).map(([zone, probability]) => (
                <li key={zone}>{zone}: {(probability * 100).toFixed(1)}%</li>
              ))}
            </ul>
            <ul className="detail-list">
              {prediction.notes.map((note) => <li key={note}>{note}</li>)}
            </ul>
          </>
        ) : (
          <div className="empty-card">Pick a kicker and goalkeeper to compare likely placement and score odds.</div>
        )}
      </section>
    </div>
  );
}

