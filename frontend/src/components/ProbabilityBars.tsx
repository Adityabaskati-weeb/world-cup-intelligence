type Props = {
  homeLabel: string;
  awayLabel: string;
  home: number;
  draw: number;
  away: number;
};

export function ProbabilityBars({ homeLabel, awayLabel, home, draw, away }: Props) {
  return (
    <div className="probability-card">
      <div className="prob-row">
        <span>{homeLabel}</span>
        <div className="prob-track">
          <div className="prob-fill prob-home" style={{ width: `${home * 100}%` }} />
        </div>
        <strong>{(home * 100).toFixed(1)}%</strong>
      </div>
      <div className="prob-row">
        <span>Draw</span>
        <div className="prob-track">
          <div className="prob-fill prob-draw" style={{ width: `${draw * 100}%` }} />
        </div>
        <strong>{(draw * 100).toFixed(1)}%</strong>
      </div>
      <div className="prob-row">
        <span>{awayLabel}</span>
        <div className="prob-track">
          <div className="prob-fill prob-away" style={{ width: `${away * 100}%` }} />
        </div>
        <strong>{(away * 100).toFixed(1)}%</strong>
      </div>
    </div>
  );
}

