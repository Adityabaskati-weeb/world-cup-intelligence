import { FormEvent, useEffect, useMemo, useState } from "react";
import { MetricCards } from "../components/MetricCards";
import { ProbabilityBars } from "../components/ProbabilityBars";
import { RefreshStatusStrip } from "../components/RefreshStatusStrip";
import { StatusMessage } from "../components/StatusMessage";
import { api, describeError, type MatchPrediction, type RefreshStatus, type TeamProfile } from "../lib/api";

const STAGES = [
  { value: "group", label: "Group stage" },
  { value: "round_of_32", label: "Round of 32" },
  { value: "round_of_16", label: "Round of 16" },
  { value: "quarterfinal", label: "Quarterfinal" },
  { value: "semifinal", label: "Semifinal" },
  { value: "final", label: "Final" },
];

function stageLabel(stage: string) {
  return STAGES.find((entry) => entry.value === stage)?.label ?? stage.replaceAll("_", " ");
}

function confidenceLabel(prediction: MatchPrediction | null) {
  if (!prediction) {
    return "Pick a fixture and frame the scenario.";
  }
  const edge = Math.abs(prediction.home_win_probability - prediction.away_win_probability);
  if (edge >= 0.22) {
    return "Clear lean";
  }
  if (edge >= 0.1) {
    return "Measured lean";
  }
  return "Tight matchup";
}

export function MatchPredictorPage() {
  const [teams, setTeams] = useState<TeamProfile[]>([]);
  const [homeTeam, setHomeTeam] = useState("");
  const [awayTeam, setAwayTeam] = useState("");
  const [stage, setStage] = useState("group");
  const [neutralSite, setNeutralSite] = useState(false);
  const [prediction, setPrediction] = useState<MatchPrediction | null>(null);
  const [refreshStatus, setRefreshStatus] = useState<RefreshStatus | null>(null);
  const [loadingTeams, setLoadingTeams] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoadingTeams(true);
      setCatalogError(null);
      setRefreshError(null);
      const [teamsResult, refreshResult] = await Promise.allSettled([api.getTeams(), api.getRefreshStatus()]);
      if (cancelled) {
        return;
      }

      if (teamsResult.status === "fulfilled") {
        const nextTeams = teamsResult.value;
        setTeams(nextTeams);
        const defaultHome = nextTeams[0]?.name ?? "";
        const defaultAway = nextTeams.find((team) => team.name !== defaultHome)?.name ?? "";
        setHomeTeam(defaultHome);
        setAwayTeam(defaultAway);
      } else {
        setTeams([]);
        setCatalogError(describeError(teamsResult.reason));
      }

      if (refreshResult.status === "fulfilled") {
        setRefreshStatus(refreshResult.value);
      } else {
        setRefreshStatus(null);
        setRefreshError(describeError(refreshResult.reason));
      }

      setLoadingTeams(false);
    };

    void load();
    return () => {
      cancelled = true;
    };
  }, [reloadKey]);

  useEffect(() => {
    setPrediction(null);
    setSubmitError(null);
  }, [awayTeam, homeTeam, neutralSite, stage]);

  const invalidReason = useMemo(() => {
    if (!teams.length) {
      return "The backend has not returned any tournament teams yet.";
    }
    if (teams.length < 2) {
      return "Need at least two backend-backed team profiles to run a prediction.";
    }
    if (!homeTeam || !awayTeam) {
      return "Select both teams to build a fixture.";
    }
    if (homeTeam === awayTeam) {
      return "Choose two different teams before running the prediction.";
    }
    return null;
  }, [awayTeam, homeTeam, teams]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (invalidReason) {
      setSubmitError(invalidReason);
      return;
    }

    setSubmitting(true);
    setSubmitError(null);
    try {
      const result = await api.predictMatch({
        home_team: homeTeam,
        away_team: awayTeam,
        neutral_site: neutralSite,
        stage,
      });
      setPrediction(result);
    } catch (nextError) {
      setPrediction(null);
      setSubmitError(describeError(nextError));
    } finally {
      setSubmitting(false);
    }
  };

  const teamLookup = useMemo(() => new Map(teams.map((team) => [team.name, team])), [teams]);
  const homeProfile = teamLookup.get(homeTeam);
  const awayProfile = teamLookup.get(awayTeam);

  const modelStats = useMemo(
    () =>
      prediction
        ? [
            { label: "Projected winner", value: prediction.projected_winner, hint: "Highest probability outcome after calibration." },
            { label: "Confidence", value: confidenceLabel(prediction), hint: "Difference between the two win probabilities." },
            { label: "Model family", value: prediction.model_version, hint: prediction.training_window.replaceAll("_", " ") },
          ]
        : [],
    [prediction],
  );

  const scenarioNotes = useMemo(
    () => [
      `${homeProfile?.confederation ?? "Unknown"} against ${awayProfile?.confederation ?? "unknown"} opposition`,
      neutralSite ? "Neutral-site assumptions are active" : "Host and travel context are active",
      `${stageLabel(stage)} scenario`,
    ],
    [awayProfile?.confederation, homeProfile?.confederation, neutralSite, stage],
  );

  const matchupBriefing = prediction
    ? `${prediction.projected_winner} carries the stronger pre-kickoff profile in this ${stageLabel(stage).toLowerCase()} scenario.`
    : "Use the predictor to stress-test a fixture before the tournament turns volatile.";

  return (
    <div className="page-grid">
      <section className="hero-panel hero-panel-large">
        <div className="hero-header">
          <div>
            <p className="eyebrow">Match Predictor</p>
            <h1>Turn a fixture into a pre-match briefing</h1>
          </div>
          <span className="section-badge">{stageLabel(stage)}</span>
        </div>
        <p className="hero-copy">
          A tournament-first prediction surface built around the same signals scouts actually discuss: Elo strength,
          recent form, rest, venue context, confederation profile, and a readable momentum layer that explains where
          the edge really comes from.
        </p>
        <div className="duel-strip">
          <article className="duel-side">
            <span className="duel-label">Home profile</span>
            <strong>{homeTeam || "Select a team"}</strong>
            <small>
              {homeProfile?.group ? `Group ${homeProfile.group}` : "Tournament team"} | {homeProfile?.confederation ?? "Unknown confederation"}
            </small>
          </article>
          <div className="duel-center">
            <span>vs</span>
            <small>{neutralSite ? "Neutral site" : "Contextual site"}</small>
          </div>
          <article className="duel-side">
            <span className="duel-label">Away profile</span>
            <strong>{awayTeam || "Select a team"}</strong>
            <small>
              {awayProfile?.group ? `Group ${awayProfile.group}` : "Tournament team"} | {awayProfile?.confederation ?? "Unknown confederation"}
            </small>
          </article>
        </div>
      </section>

      {refreshStatus ? (
        <RefreshStatusStrip
          status={refreshStatus}
          title="Signal readiness"
          subtitle="Matchflow exposes which data layers are live, snapshot-backed, or waiting for operator attention before you trust the pre-match read."
          compact
        />
      ) : refreshError ? (
        <StatusMessage title="Signal readiness is unavailable." tone="info">
          {refreshError}
        </StatusMessage>
      ) : null}

      <div className="page-grid two-column page-section-grid">
        <section className="panel">
          <div className="section-header">
            <div>
              <h2>Build the scenario</h2>
              <small>Choose the fixture and decide how much tournament context matters.</small>
            </div>
            <button
              className="ghost-button"
              type="button"
              onClick={() => {
                setHomeTeam(awayTeam);
                setAwayTeam(homeTeam);
              }}
              disabled={!homeTeam || !awayTeam}
            >
              Swap teams
            </button>
          </div>

          {catalogError ? (
            <div className="section-stack">
              <StatusMessage title="Team catalog could not be loaded." tone="error">
                {catalogError}
              </StatusMessage>
              <button className="ghost-button" type="button" onClick={() => setReloadKey((value) => value + 1)}>
                Retry team catalog
              </button>
            </div>
          ) : null}

          {submitError ? (
            <StatusMessage title="Prediction workflow hit an issue." tone="error">
              {submitError}
            </StatusMessage>
          ) : null}

          {loadingTeams ? (
            <StatusMessage title="Loading team selector..." tone="loading">
              Pulling tournament teams and prediction context.
            </StatusMessage>
          ) : !teams.length ? (
            <StatusMessage title="No teams are available yet." tone="info">
              The backend did not return any team profiles for this tournament cycle.
            </StatusMessage>
          ) : (
            <form className="stack-form" onSubmit={handleSubmit}>
              <label>
                Home team
                <select value={homeTeam} onChange={(event) => setHomeTeam(event.target.value)}>
                  {teams.map((team) => (
                    <option key={team.team_id} value={team.name}>
                      {team.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Away team
                <select value={awayTeam} onChange={(event) => setAwayTeam(event.target.value)}>
                  {teams.map((team) => (
                    <option key={team.team_id} value={team.name}>
                      {team.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Tournament stage
                <select value={stage} onChange={(event) => setStage(event.target.value)}>
                  {STAGES.map((entry) => (
                    <option key={entry.value} value={entry.value}>
                      {entry.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="toggle-row">
                <input type="checkbox" checked={neutralSite} onChange={(event) => setNeutralSite(event.target.checked)} />
                <span>Treat this as a neutral-site fixture</span>
              </label>
              {invalidReason ? (
                <div className="info-callout">
                  <strong>Fix the matchup first</strong>
                  <p>{invalidReason}</p>
                </div>
              ) : null}
              <button className="accent-button" type="submit" disabled={submitting || Boolean(invalidReason)}>
                {submitting ? "Running model..." : "Run prediction"}
              </button>
            </form>
          )}
        </section>

        <section className="panel">
          <div className="section-header">
            <div>
              <h2>{prediction ? `${prediction.projected_winner} edge` : "Matchup outlook"}</h2>
              <small>{matchupBriefing}</small>
            </div>
            {prediction ? <span className="section-badge">{prediction.mode.replaceAll("_", " ")}</span> : null}
          </div>

          {prediction ? (
            <>
              <MetricCards items={modelStats} compact />
              <div className="insight-banner">
                <strong>{confidenceLabel(prediction)}</strong>
                <p>
                  {homeTeam} against {awayTeam}. {scenarioNotes.join(" | ")}.
                </p>
              </div>
              <section className="momentum-panel">
                <div className="momentum-head">
                  <div>
                    <span className="duel-label">Momentum read</span>
                    <strong>{prediction.momentum.edge_team}</strong>
                  </div>
                  <div className="momentum-meta">
                    <span>{prediction.momentum.confidence_band}</span>
                    <small>{prediction.momentum.volatility} volatility</small>
                  </div>
                </div>
                <div className="momentum-meter" aria-label="Momentum swing meter">
                  <div className="momentum-fill" style={{ width: `${prediction.momentum.swing_index}%` }} />
                </div>
                <p className="panel-copy">{prediction.momentum.summary}</p>
              </section>
              <ProbabilityBars
                homeLabel={homeTeam}
                awayLabel={awayTeam}
                home={prediction.home_win_probability}
                draw={prediction.draw_probability}
                away={prediction.away_win_probability}
              />
              <div className="reasoning-grid">
                {prediction.factors.map((factor) => (
                  <article key={factor.key} className="factor-card">
                    <div className="factor-card-head">
                      <div>
                        <span className="duel-label">{factor.label}</span>
                        <strong>{factor.edge_team}</strong>
                      </div>
                      <span className="section-badge">Impact {Math.round(factor.impact_score * 100)}</span>
                    </div>
                    <div className="factor-meter" aria-hidden="true">
                      <div className="factor-fill" style={{ width: `${Math.max(8, factor.impact_score * 100)}%` }} />
                    </div>
                    <p>{factor.summary}</p>
                  </article>
                ))}
              </div>
              <div className="detail-block">
                <h3>Why the match tilts this way</h3>
                <ul className="detail-list detail-list-tight">
                  {prediction.narrative.map((note) => (
                    <li key={note}>
                      <strong>Story</strong>
                      <span>{note}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </>
          ) : (
            <StatusMessage title="Pick a matchup to generate probabilities." tone="info">
              The briefing card will turn this fixture into a momentum read with probabilities, impact factors, and a
              football-first narrative instead of a bare model score.
            </StatusMessage>
          )}
        </section>
      </div>
    </div>
  );
}
