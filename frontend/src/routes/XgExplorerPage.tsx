import { startTransition, useEffect, useState } from "react";
import { api, type PlayerProfile, type TeamProfile, type XgProfile } from "../lib/api";
import { ShotMap } from "../components/ShotMap";

export function XgExplorerPage() {
  const [teams, setTeams] = useState<TeamProfile[]>([]);
  const [players, setPlayers] = useState<PlayerProfile[]>([]);
  const [teamSelection, setTeamSelection] = useState("brazil");
  const [playerSelection, setPlayerSelection] = useState("mbappe");
  const [profile, setProfile] = useState<XgProfile | null>(null);

  useEffect(() => {
    void api.getTeams().then(setTeams);
    void api.getPlayers().then((payload) => setPlayers(payload.players));
  }, []);

  return (
    <div className="page-grid two-column">
      <section className="panel">
        <p className="eyebrow">xG Explorer</p>
        <h2>Where the best chances actually come from</h2>
        <div className="stack-form">
          <label>
            Team dashboard
            <select
              value={teamSelection}
              onChange={(event) =>
                startTransition(() => {
                  setTeamSelection(event.target.value);
                  void api.getTeamXg(event.target.value).then(setProfile);
                })
              }
            >
              <option value="brazil">Brazil</option>
              <option value="france">France</option>
              <option value="england">England</option>
            </select>
          </label>
          <label>
            Player dashboard
            <select
              value={playerSelection}
              onChange={(event) =>
                startTransition(() => {
                  setPlayerSelection(event.target.value);
                  void api.getPlayerXg(event.target.value).then(setProfile);
                })
              }
            >
              {players.map((player) => <option key={player.player_id} value={player.player_id}>{player.player_name}</option>)}
            </select>
          </label>
          <div className="button-row">
            <button className="accent-button" onClick={() => void api.getTeamXg(teamSelection).then(setProfile)}>Load team xG</button>
            <button className="ghost-button" onClick={() => void api.getPlayerXg(playerSelection).then(setProfile)}>Load player xG</button>
          </div>
        </div>
      </section>

      <section className="panel">
        {profile ? (
          <>
            <div className="section-header">
              <h2>{profile.label}</h2>
              <small>{profile.scope} • {profile.sample_size} shots</small>
            </div>
            <ShotMap shots={profile.shots} />
            <div className="hero-stats compact">
              <div><span>Total xG</span><strong>{profile.total_xg.toFixed(2)}</strong></div>
              <div><span>Goals</span><strong>{profile.actual_goals}</strong></div>
              <div><span>Finishing delta</span><strong>{profile.finishing_delta.toFixed(2)}</strong></div>
            </div>
            <ul className="detail-list">
              {profile.zones.map((zone) => (
                <li key={zone.zone}>{zone.zone}: {zone.shots} shots • {zone.xg.toFixed(2)} xG</li>
              ))}
            </ul>
          </>
        ) : (
          <div className="empty-card">Load a team or player to inspect shot quality by zone.</div>
        )}
      </section>
    </div>
  );
}

