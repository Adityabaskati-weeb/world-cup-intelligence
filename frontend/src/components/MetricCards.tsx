type MetricCard = {
  label: string;
  value: string;
  hint?: string;
};

type Props = {
  items: MetricCard[];
  compact?: boolean;
};

export function MetricCards({ items, compact = false }: Props) {
  return (
    <div className={`metric-grid${compact ? " compact" : ""}`}>
      {items.map((item) => (
        <div key={`${item.label}-${item.value}`} className="metric-card">
          <span>{item.label}</span>
          <strong>{item.value}</strong>
          {item.hint ? <small>{item.hint}</small> : null}
        </div>
      ))}
    </div>
  );
}
