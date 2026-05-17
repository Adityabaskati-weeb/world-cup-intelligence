import { startTransition, useEffect, useMemo, useState } from "react";
import { MetricCards } from "../components/MetricCards";
import { RefreshStatusStrip } from "../components/RefreshStatusStrip";
import { ShotMap } from "../components/ShotMap";
import { StatusMessage } from "../components/StatusMessage";
import { api, describeError, type PlayerProfile, type RefreshStatus, type XgCatalogTeam, type XgProfile } from "../lib/api";

type Scope = "team" | "player";

function finishingStory(profile: XgProfile | null) {
  if (!profile) {
    return "";
  }
  if (profile.finishing_delta > 0.35) {
    return `${profile.label} is currently finishing above expectation.`;
  }
  if (profile.finishing_delta < -0.35) {
    return `${profile.label} is leaving goals behind relative to chance quality.`;
  }
  return `${profile.label} is converting chances close to expectation.`;
}

function trustLabel(sampleSize: number) {
  if (sampleSize >= 24) {
    return "High-signal sample";
  }
  if (sampleSize >= 12) {
    return "Useful sample";
  }
  return "Thin sample";
}

function topSituation(profile: XgProfile | null) {
  if (!profile?.shots.length) {
    return null;
  }
  const counts = new Map<string, number>();
  profile.shots.forEach((shot) => {
    counts.set(shot.situation, (counts.get(shot.situation) ?? 0) + 1);
  });
  return [...counts.entries()].sort((left, right) => right[1] - left[1])[0]?.[0] ?? null;
}

function bodyPartLean(profile: XgProfile | null) {
  if (!profile?.shots.length) {
    return null;
  }
  const counts = new Map<string, number>();
  profile.shots.forEach((shot) => {
    counts.set(shot.body_part, (counts.get(shot.body_part) ?? 0) + 1);
  });
  return [...counts.entries()].sort((left, right) => right[1] - left[1])[0]?.[0] ?? null;
}

export function XgExplorerPage() {
  const [teams, setTeams] = useState<XgCatalogTeam[]>([]);
  const [players, setPlayers] = useState<PlayerProfile[]>([]);
  const [scope, setScope] = useState<Scope>("team");
  const [teamSelection, setTeamSelection] = useState("");
  const [playerSelection, setPlayerSelection] = useState("");
  const [profile, setProfile] = useState<XgProfile | null>(null);
  const [refreshStatus, setRefreshStatus] = useState<RefreshStatus | null>(null);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [profileLoading, setProfileLoading] = useState(false);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setCatalogLoading(true);
      setCatalogError(null);
      setProfileError(null);
      setRefreshError(null);
      const [catalogResult, pulseResult] = await Promise.allSettled([api.getXgCatalog(), api.getRefreshStatus()]);
      if (cancelled) {
        return;
      }

      if (catalogResult.status === "fulfilled") {
        const catalog = catalogResult.value;
        setTeams(catalog.teams);
        setPlayers(catalog.players);

        const defaultTeam = catalog.teams[0]?.team_id ?? "";
        const defaultPlayer = catalog.players[0]?.player_id ?? "";
        setTeamSelection(defaultTeam);
        setPlayerSelection(defaultPlayer);
        setScope(defaultTeam ? "team" : defaultPlayer ? "player" : "team");

        if (defaultTeam) {
          setProfileLoading(true);
          try {
            const nextProfile = await api.getTeamXg(defaultTeam);
            if (!cancelled) {
              setProfile(nextProfile);
            }
          } catch (nextError) {
            if (!cancelled) {
              setProfile(null);
              setProfileError(describeError(nextError));
            }
          } finally {
            if (!cancelled) {
              setProfileLoading(false);
            }
          }
        } else {
          setProfile(null);
        }
      } else {
        setTeams([]);
        setPlayers([]);
        setProfile(null);
        setCatalogError(describeError(catalogResult.reason));
      }

      if (pulseResult.status === "fulfilled") {
        setRefreshStatus(pulseResult.value);
      } else {
        setRefreshStatus(null);
        setRefreshError(describeError(pulseResult.reason));
      }

      if (!cancelled) {
        setCatalogLoading(false);
        setProfileLoading(false);
      }
    };

    void load();
    return () => {
      cancelled = true;
    };
  }, [reloadKey]);

  const loadProfile = async (nextScope: Scope, targetId: string) => {
    setScope(nextScope);
    setProfile(null);
    setProfileLoading(true);
    setProfileError(null);

    if (!targetId) {
      setProfileLoading(false);
      return;
    }

    try {
      const nextProfile = nextScope === "team" ? await api.getTeamXg(targetId) : await api.getPlayerXg(targetId);
      setProfile(nextProfile);
    } catch (nextError) {
      setProfile(null);
      setProfileError(describeError(nextError));
    } finally {
      setProfileLoading(false);
    }
  };

  const headlineStats = useMemo(
    () =>
      profile
        ? [
            { label: "Total xG", value: profile.total_xg.toFixed(2), hint: "Sum of modeled chance quality." },
            { label: "Goals", value: `${profile.actual_goals}`, hint: "Actual conversion from these shots." },
            { label: "Finishing delta", value: profile.finishing_delta.toFixed(2), hint: "Goals minus expected goals." },
            { label: "Tracked shots", value: `${profile.sample_size}`, hint: profile.training_window.replaceAll("_", " ") },
          ]
        : [],
    [profile],
  );

  const leadZone = useMemo(() => {
    if (!profile?.zones.length) {
      return null;
    }
    return [...profile.zones].sort((left, right) => right.xg - left.xg)[0];
  }, [profile]);

  const leadZoneShare = useMemo(() => {
    if (!profile || !leadZone || profile.total_xg <= 0) {
      return 0;
    }
    return Math.min(100, (leadZone.xg / profile.total_xg) * 100);
  }, [leadZone, profile]);

  const dominantSituation = useMemo(() => topSituation(profile), [profile]);
  const dominantBodyPart = useMemo(() => bodyPartLean(profile), [profile]);

  const tacticalCards = useMemo(() => {
    if (!profile) {
      return [];
    }
    return [
      {
        label: "Signal trust",
        value: trustLabel(profile.sample_size),
        hint: `${profile.sample_size} tracked shots are informing this view.`,
      },
      {
        label: "Primary chance source",
        value: dominantSituation ?? "Mixed phases",
        hint: "The most common game situation behind the recorded shots.",
      },
      {
        label: "Finishing posture",
        value:
          profile.finishing_delta > 0.35
            ? "Running hot"
            : profile.finishing_delta < -0.35
              ? "Leaving chances behind"
              : "Close to expectation",
        hint: "Goals scored relative to the xG total.",
      },
    ];
  }, [dominantSituation, profile]);

  const shotNarratives = useMemo(() => {
    if (!profile) {
      return [];
    }
    const zoneStory = leadZone
      ? `${profile.label} concentrates its cleanest looks in ${leadZone.zone}, which accounts for ${leadZoneShare.toFixed(0)}% of the xG load.`
      : `${profile.label} is distributing its xG across multiple areas rather than leaning on one finishing pocket.`;
    const phaseStory = dominantSituation
      ? `${dominantSituation} is the strongest repeatable phase in this sample, which hints at how the attack is manufacturing danger.`
      : "The sample is too mixed to isolate one clear phase-of-play signature.";
    const bodyStory = dominantBodyPart
      ? `${dominantBodyPart} is the dominant finishing surface here, a useful cue when reading the shot profile under pressure.`
      : "Body-part usage is balanced enough that no single finishing surface dominates.";
    const tournamentStory =
      profile.finishing_delta > 0.35
        ? "If this finishing level holds into knockout football, the attack can turn marginal territory into real scoreboard damage."
        : profile.finishing_delta < -0.35
          ? "The chance creation is healthier than the goal return, so the tournament swing may come if finishing normalizes."
          : "This profile is stable enough to trust as a tournament fingerprint rather than a short hot streak.";
    return [zoneStory, phaseStory, bodyStory, tournamentStory];
  }, [dominantBodyPart, dominantSituation, leadZone, leadZoneShare, profile]);

  const emptyCatalogMessage = useMemo(() => {
    if (!teams.length && !players.length) {
      return "The backend returned no xG team or player catalog entries for this tournament cycle.";
    }
    if (!teams.length) {
      return "The team xG catalog is empty, so only player-level exploration is currently available.";
    }
    if (!players.length) {
      return "The player xG catalog is empty, so only team-level exploration is currently available.";
    }
    return null;
  }, [players.length, teams.length]);

  return (
    <div className="page-grid">
      <section className="hero-panel hero-panel-large">
        <div className="hero-header">
          <div>
            <p className="eyebrow">xG Explorer</p>
            <h1>Read where the tournament&apos;s best chances are coming from</h1>
          </div>
          <span className="section-badge">{scope === "team" ? "Team dashboard" : "Player dashboard"}</span>
        </div>
        <p className="hero-copy">
          Shift between team and player views, inspect the shot map, and turn expected goals into a more useful
          finishing story instead of a single headline number. Matchflow treats xG like territory, shot craft, and
          tournament danger, not just a stat line.
        </p>
      </section>

      {refreshStatus ? (
        <RefreshStatusStrip
          status={refreshStatus}
          title="Intelligence pulse"
          subtitle="This xG surface inherits the same freshness and signal-trust layer as the rest of the platform."
          compact
        />
      ) : refreshError ? (
        <StatusMessage title="Intelligence pulse is unavailable." tone="info">
          {refreshError}
        </StatusMessage>
      ) : null}

      <div className="page-grid two-column page-section-grid">
        <section className="panel">
          <div className="section-header">
            <div>
              <h2>Choose the lens</h2>
              <small>Switch between team-wide territory and individual finishing profiles.</small>
            </div>
          </div>

          {catalogError ? (
            <div className="section-stack">
              <StatusMessage title="xG catalog could not be loaded." tone="error">
                {catalogError}
              </StatusMessage>
              <button className="ghost-button" type="button" onClick={() => setReloadKey((value) => value + 1)}>
                Retry xG catalog
              </button>
            </div>
          ) : null}

          {profileError ? (
            <StatusMessage title="The selected xG profile could not be loaded." tone="error">
              {profileError}
            </StatusMessage>
          ) : null}

          {catalogLoading ? (
            <StatusMessage title="Loading xG catalog..." tone="loading">
              Pulling tracked teams, players, and their shot maps.
            </StatusMessage>
          ) : emptyCatalogMessage ? (
            <StatusMessage title="xG coverage is incomplete." tone="info">
              {emptyCatalogMessage}
            </StatusMessage>
          ) : (
            <div className="stack-form">
              <div className="segmented-row">
                <button
                  className={`ghost-button${scope === "team" ? " selected" : ""}`}
                  onClick={() => void loadProfile("team", teamSelection)}
                  type="button"
                  aria-pressed={scope === "team"}
                  disabled={!teams.length || !teamSelection}
                >
                  Team view
                </button>
                <button
                  className={`ghost-button${scope === "player" ? " selected" : ""}`}
                  onClick={() => void loadProfile("player", playerSelection)}
                  type="button"
                  aria-pressed={scope === "player"}
                  disabled={!players.length || !playerSelection}
                >
                  Player view
                </button>
              </div>
              <label>
                Team dashboard
                <select
                  value={teamSelection}
                  onChange={(event) =>
                    startTransition(() => {
                      setTeamSelection(event.target.value);
                      void loadProfile("team", event.target.value);
                    })
                  }
                  disabled={!teams.length}
                >
                  {teams.map((team) => (
                    <option key={team.team_id} value={team.team_id}>
                      {team.label}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Player dashboard
                <select
                  value={playerSelection}
                  onChange={(event) =>
                    startTransition(() => {
                      setPlayerSelection(event.target.value);
                      void loadProfile("player", event.target.value);
                    })
                  }
                  disabled={!players.length}
                >
                  {players.map((player) => (
                    <option key={player.player_id} value={player.player_id}>
                      {player.player_name} | {player.team}
                    </option>
                  ))}
                </select>
              </label>
              <div className="info-callout">
                <strong>
                  {teams.length} tracked teams | {players.length} tracked player profiles
                </strong>
                <p>
                  Compare shot quality against actual finishing to spot volume shooters, elite finishers, and teams
                  living off low-value looks.
                </p>
              </div>
            </div>
          )}
        </section>

        <section className="panel panel-wide">
          {profileLoading ? (
            <StatusMessage title="Rendering shot map..." tone="loading">
              Building the selected xG profile and zone summary.
            </StatusMessage>
          ) : profile ? (
            <>
              <div className="section-header">
                <div>
                  <h2>{profile.label}</h2>
                  <small>
                    {profile.scope === "team" ? "Team territory view" : "Individual finishing view"} | {profile.team}
                  </small>
                </div>
                <span className="section-badge">{profile.model_version}</span>
              </div>
              <MetricCards items={headlineStats} compact />
              <div className="analysis-rail">
                <div className="analysis-main">
                  <MetricCards items={tacticalCards} compact />
                  <ShotMap shots={profile.shots} />
                  <div className="legend-row">
                    <span>
                      <i className="legend-dot goal" /> Goal
                    </span>
                    <span>
                      <i className="legend-dot miss" /> Non-goal shot
                    </span>
                    <span>Circle size scales with xG</span>
                  </div>
                </div>
                <aside className="analysis-aside">
                  <div className="insight-banner">
                    <strong>Finishing read</strong>
                    <p>{finishingStory(profile)}</p>
                  </div>
                  {leadZone ? (
                    <div className="info-callout">
                      <strong>Primary threat pocket</strong>
                      <p>
                        {leadZone.zone} has produced {leadZone.xg.toFixed(2)} xG across {leadZone.shots} shots, or{" "}
                        {leadZoneShare.toFixed(0)}% of the total threat load.
                      </p>
                    </div>
                  ) : null}
                  <div className="info-callout">
                    <strong>Tournament implication</strong>
                    <p>{shotNarratives[3] ?? "Tournament implications will appear once the shot profile is loaded."}</p>
                  </div>
                </aside>
              </div>
              <div className="detail-block">
                <h3>Football reading</h3>
                <ul className="detail-list detail-list-tight">
                  {shotNarratives.slice(0, 3).map((note) => (
                    <li key={note}>
                      <strong>Insight</strong>
                      <span>{note}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="detail-block">
                <h3>Zone breakdown</h3>
                <div className="zone-list">
                  {profile.zones.map((zone) => {
                    const share = profile.total_xg > 0 ? Math.min(100, (zone.xg / profile.total_xg) * 100) : 0;
                    return (
                      <article key={zone.zone} className="zone-item">
                        <div className="zone-item-head">
                          <strong>{zone.zone}</strong>
                          <span>
                            {zone.shots} shots | {zone.xg.toFixed(2)} xG
                          </span>
                        </div>
                        <div className="zone-meter">
                          <div className="zone-meter-fill" style={{ width: `${share}%` }} />
                        </div>
                      </article>
                    );
                  })}
                </div>
              </div>
            </>
          ) : (
            <StatusMessage title="Select a team or player to inspect shot quality." tone="info">
              The xG dashboard will show shot maps, zone summaries, and finishing deltas once a profile is selected.
            </StatusMessage>
          )}
        </section>
      </div>
    </div>
  );
}
