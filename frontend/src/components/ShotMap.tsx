import type { XgPoint } from "../lib/api";

type Props = {
  shots: XgPoint[];
};

export function ShotMap({ shots }: Props) {
  return (
    <svg viewBox="0 0 100 68" className="shot-map" role="img" aria-label="Shot map">
      <rect x="0" y="0" width="100" height="68" rx="4" className="pitch-grass" />
      <rect x="82" y="18" width="18" height="32" className="pitch-box" />
      <rect x="94" y="28" width="6" height="12" className="pitch-goal" />
      <circle cx="88" cy="34" r="0.6" className="pitch-spot" />
      {shots.map((shot) => (
        <g key={`${shot.player_id}-${shot.minute}-${shot.x}-${shot.y}`}>
          <circle
            cx={shot.x}
            cy={shot.y}
            r={Math.max(1.4, shot.xg * 7)}
            className={shot.outcome === "Goal" ? "shot-goal" : "shot-miss"}
          />
          <title>{`${shot.player_name} ${shot.minute}' xG ${shot.xg}`}</title>
        </g>
      ))}
    </svg>
  );
}

