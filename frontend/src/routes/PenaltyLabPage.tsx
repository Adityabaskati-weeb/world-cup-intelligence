import { FormEvent, useEffect, useMemo, useState } from "react";
import { MetricCards } from "../components/MetricCards";
import { RefreshStatusStrip } from "../components/RefreshStatusStrip";
import { StatusMessage } from "../components/StatusMessage";
import { api, describeError, type KeeperProfile, type KickerProfile, type PenaltyPrediction, type RefreshStatus } from "../lib/api";

function pressureLabel(pressure: number) {
  if (pressure >= 0.9) {
    return "Sudden-death intensity";
  }
  if (pressure >= 0.75) {
    return "Knockout pressure";
  }
  if (pressure >= 0.6) {
    return "Competitive but controlled";
  }
  return "Training-ground rhythm";
}

function trustBand(sampleSize: number) {
  if (sampleSize >= 20) {
    return "High trust";
  }
  if (sampleSize >= 12) {
    return "Useful trust";
  }
  return "Thin trust";
}

export function PenaltyLabPage() {
  const [kickers, setKickers] = useState<KickerProfile[]>([]);
  const [keepers, setKeepers] = useState<KeeperProfile[]>([]);
  const [playerId, setPlayerId] = useState("");
  const [keeperId, setKeeperId] = useState("");
  const [pressure, setPressure] = useState(0.85);
  const [prediction, setPrediction] = useState<PenaltyPrediction | null>(null);
  const [refreshStatus, setRefreshStatus] = useState<RefreshStatus | null>(null);
  const [loadingCatalog, setLoadingCatalog] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoadingCatalog(true);
      setCatalogError(null);
      setRefreshError(null);
      const [catalogResult, pulseResult] = await Promise.allSettled([api.getPlayers(), api.getRefreshStatus()]);
      if (cancelled) {
        return;
      }

      if (catalogResult.status === "fulfilled") {
        const payload = catalogResult.value;
        setKickers(payload.kickers);
        setKeepers(payload.keepers);
        setPlayerId(payload.kickers[0]?.player_id ?? "");
        setKeeperId(payload.keepers[0]?.keeper_id ?? "");
      } else {
        setKickers([]);
        setKeepers([]);
        setCatalogError(describeError(catalogResult.reason));
      }

      if (pulseResult.status === "fulfilled") {
        setRefreshStatus(pulseResult.value);
      } else {
        setRefreshStatus(null);
        setRefreshError(describeError(pulseResult.reason));
      }

      if (!cancelled) {
        setLoadingCatalog(false);
      }
    };

    void load();
    return () => {
      cancelled = true;
    };
  }, [reloadKey]);

  useEffect(() => {
    setPrediction(null);
    setSubmitError(null);
  }, [keeperId, playerId, pressure]);

  const invalidReason = useMemo(() => {
    if (!kickers.length) {
      return "The backend has not returned any tracked kickers yet.";
    }
    if (!keepers.length) {
      return "The backend has not returned any tracked keepers yet.";
    }
    if (!playerId || !keeperId) {
      return "Select both a kicker and a keeper to compare the duel.";
    }
    return null;
  }, [keeperId, keepers.length, kickers.length, playerId]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (invalidReason) {
      setSubmitError(invalidReason);
      return;
    }

    setSubmitting(true);
    setSubmitError(null);
    try {
      const result = await api.predictPenalty({
        player_id: playerId,
        keeper_id: keeperId,
        context: { pressure, tournament_stage: "knockout" },
      });
      setPrediction(result);
    } catch (nextError) {
      setPrediction(null);
      setSubmitError(describeError(nextError));
    } finally {
      setSubmitting(false);
    }
  };

  const kicker = kickers.find((entry) => entry.player_id === playerId);
  const keeper = keepers.find((entry) => entry.keeper_id === keeperId);

  const summaryCards = useMemo(
    () =>
      prediction
        ? [
            { label: "Conversion", value: `${(prediction.scoring_probability * 100).toFixed(1)}%`, hint: "Expected score probability." },
            { label: "Likely zone", value: prediction.likely_target_zone, hint: "Highest placement probability from the model." },
            { label: "Pressure read", value: pressureLabel(pressure), hint: "Current scenario intensity." },
          ]
        : [],
    [prediction, pressure],
  );

  const orderedZones = useMemo(
    () =>
      prediction
        ? Object.entries(prediction.target_zone_probabilities).sort((left, right) => right[1] - left[1])
        : [],
    [prediction],
  );

  const zoneConcentration = orderedZones[0]?.[1] ?? 0;

  const duelCards = useMemo(
    () =>
      prediction
        ? [
            {
              label: "Trust band",
              value: trustBand(prediction.sample_size),
              hint: `${prediction.sample_size} historical attempts are informing this duel read.`,
            },
            {
              label: "Volatility",
              value:
                pressure >= 0.85 && prediction.scoring_probability <= 0.76
                  ? "Keeper live in duel"
                  : pressure >= 0.85
                    ? "Pressure but kicker edge"
                    : "Controlled duel",
              hint: "Combines tournament pressure with the model's expected conversion rate.",
            },
            {
              label: "Placement grip",
              value: `${(zoneConcentration * 100).toFixed(0)}%`,
              hint: "Share owned by the most likely target zone.",
            },
          ]
        : [],
    [prediction, pressure, zoneConcentration],
  );

  const duelNarratives = useMemo(() => {
    if (!prediction) {
      return [];
    }
    const pressureStory =
      pressure >= 0.85
        ? "This is framed like a genuine knockout kick, so composure and keeper anticipation carry more weight than in a low-stress sample."
        : "The pressure dial is below sudden-death level, so the read leans more on technique and historical preference than nerves.";
    const placementStory =
      zoneConcentration >= 0.4
        ? `${kicker?.player_name ?? "The taker"} shows a fairly strong pull toward ${prediction.likely_target_zone}, giving the keeper one zone to fear most.`
        : `${kicker?.player_name ?? "The taker"} spreads placement enough that the keeper cannot overcommit to a single corner.`;
    const upsetStory =
      prediction.scoring_probability < 0.72
        ? `${keeper?.keeper_name ?? "The keeper"} has enough leverage in this duel that an upset save would not be surprising.`
        : `${kicker?.player_name ?? "The taker"} still keeps the cleaner edge, but the shootout can swing if the first read is guessed correctly.`;
    const tournamentStory =
      pressure >= 0.85
        ? "In tournament terms, this is the kind of duel that can reroute a whole knockout path in one touch."
        : "In tournament terms, this reads more like a strong favorite trying to avoid inviting chaos.";
    return [pressureStory, placementStory, upsetStory, tournamentStory];
  }, [kicker?.player_name, keeper?.keeper_name, prediction, pressure, zoneConcentration]);

  return (
    <div className="page-grid">
      <section className="hero-panel hero-panel-large">
        <div className="hero-header">
          <div>
            <p className="eyebrow">Penalty Lab</p>
            <h1>Study the duel, not just the shot</h1>
          </div>
          <span className="section-badge">{pressureLabel(pressure)}</span>
        </div>
        <p className="hero-copy">
          Pair a taker with a goalkeeper, dial up the pressure, and turn the shootout into a scouting decision rather
          than a coin flip. The goal is to explain where the duel bends, not just estimate whether the ball goes in.
        </p>
        <div className="duel-strip">
          <article className="duel-side">
            <span className="duel-label">Kicker</span>
            <strong>{kicker?.player_name ?? "Select a taker"}</strong>
            <small>
              {kicker?.team ?? "Tournament profile"}
              {kicker?.preferred_foot ? ` | ${kicker.preferred_foot} foot` : ""}
            </small>
          </article>
          <div className="duel-center">
            <span>vs</span>
            <small>{pressure.toFixed(2)} pressure input</small>
          </div>
          <article className="duel-side">
            <span className="duel-label">Keeper</span>
            <strong>{keeper?.keeper_name ?? "Select a keeper"}</strong>
            <small>{keeper?.team ?? "Tournament profile"}</small>
          </article>
        </div>
      </section>

      {refreshStatus ? (
        <RefreshStatusStrip
          status={refreshStatus}
          title="Duel intelligence pulse"
          subtitle="Penalty scouting stays honest about source freshness and sample trust before you read a shootout edge."
          compact
        />
      ) : refreshError ? (
        <StatusMessage title="Duel intelligence pulse is unavailable." tone="info">
          {refreshError}
        </StatusMessage>
      ) : null}

      <div className="page-grid two-column page-section-grid">
        <section className="panel">
          <div className="section-header">
            <div>
              <h2>Build the penalty duel</h2>
              <small>Pick the matchup and decide how much tournament tension you want to simulate.</small>
            </div>
          </div>

          {catalogError ? (
            <div className="section-stack">
              <StatusMessage title="Penalty catalog could not be loaded." tone="error">
                {catalogError}
              </StatusMessage>
              <button className="ghost-button" type="button" onClick={() => setReloadKey((value) => value + 1)}>
                Retry penalty catalog
              </button>
            </div>
          ) : null}

          {submitError ? (
            <StatusMessage title="Penalty comparison failed." tone="error">
              {submitError}
            </StatusMessage>
          ) : null}

          {loadingCatalog ? (
            <StatusMessage title="Loading penalty profiles..." tone="loading">
              Pulling tracked kickers, keepers, and save-bias context.
            </StatusMessage>
          ) : !kickers.length || !keepers.length ? (
            <StatusMessage title="Penalty profiles are incomplete." tone="info">
              Matchflow needs both tracked kickers and tracked keepers from the backend before this duel can run.
            </StatusMessage>
          ) : (
            <form className="stack-form" onSubmit={handleSubmit}>
              <label>
                Kicker
                <select value={playerId} onChange={(event) => setPlayerId(event.target.value)}>
                  {kickers.map((player) => (
                    <option key={player.player_id} value={player.player_id}>
                      {player.player_name}
                      {player.team ? ` | ${player.team}` : ""}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Keeper
                <select value={keeperId} onChange={(event) => setKeeperId(event.target.value)}>
                  {keepers.map((nextKeeper) => (
                    <option key={nextKeeper.keeper_id} value={nextKeeper.keeper_id}>
                      {nextKeeper.keeper_name}
                      {nextKeeper.team ? ` | ${nextKeeper.team}` : ""}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Pressure level: {pressure.toFixed(2)}
                <input
                  className="range-input"
                  type="range"
                  min="0.45"
                  max="0.95"
                  step="0.05"
                  value={pressure}
                  onChange={(event) => setPressure(Number(event.target.value))}
                />
              </label>
              <div className="info-callout">
                <strong>
                  {kickers.length} tracked kickers | {keepers.length} tracked keepers
                </strong>
                <p>
                  {invalidReason ?? `${pressureLabel(pressure)}. Use higher pressure to mimic knockout or shootout moments.`}
                </p>
              </div>
              <button className="accent-button" type="submit" disabled={submitting || Boolean(invalidReason)}>
                {submitting ? "Comparing..." : "Compare matchup"}
              </button>
            </form>
          )}
        </section>

        <section className="panel panel-wide">
          {prediction ? (
            <>
              <div className="section-header">
                <div>
                  <h2>Penalty matchup outlook</h2>
                  <small>
                    {kicker?.player_name ?? prediction.player_id} against {keeper?.keeper_name ?? prediction.keeper_id}
                  </small>
                </div>
                <span className="section-badge">{prediction.model_version}</span>
              </div>
              <MetricCards items={summaryCards} compact />
              <div className="insight-banner">
                <strong>{(prediction.scoring_probability * 100).toFixed(1)}% chance to score</strong>
                <p>
                  {prediction.scoring_probability >= 0.75
                    ? "The taker keeps the edge in this state."
                    : "This duel is close enough for the keeper to influence the outcome."}
                </p>
              </div>
              <MetricCards items={duelCards} compact />
              <div className="detail-block">
                <h3>Duel reading</h3>
                <ul className="detail-list detail-list-tight">
                  {duelNarratives.slice(0, 3).map((note) => (
                    <li key={note}>
                      <strong>Insight</strong>
                      <span>{note}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="detail-block">
                <h3>Placement map</h3>
                <div className="zone-list">
                  {orderedZones.map(([zone, probability]) => (
                    <article key={zone} className="zone-item">
                      <div className="zone-item-head">
                        <strong>{zone}</strong>
                        <span>{(probability * 100).toFixed(1)}%</span>
                      </div>
                      <div className="zone-meter">
                        <div className="zone-meter-fill zone-meter-penalty" style={{ width: `${probability * 100}%` }} />
                      </div>
                    </article>
                  ))}
                </div>
              </div>
              <div className="info-callout">
                <strong>Tournament implication</strong>
                <p>{duelNarratives[3] ?? "Tournament context will appear once the duel is loaded."}</p>
              </div>
              <div className="detail-block">
                <h3>Scout notes</h3>
                <ul className="detail-list">
                  {prediction.notes.map((note) => (
                    <li key={note}>{note}</li>
                  ))}
                </ul>
              </div>
            </>
          ) : (
            <StatusMessage title="Choose a kicker and keeper to compare the duel." tone="info">
              The result panel will show score probability, placement tendencies, and matchup notes for the selected duel.
            </StatusMessage>
          )}
        </section>
      </div>
    </div>
  );
}
