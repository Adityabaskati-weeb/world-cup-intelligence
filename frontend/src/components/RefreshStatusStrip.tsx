import { type RefreshStatus } from "../lib/api";

type RefreshStatusStripProps = {
  status: RefreshStatus | null;
  title: string;
  subtitle: string;
  compact?: boolean;
};

function formatTimestamp(value?: string | null) {
  if (!value) {
    return "Timestamp unavailable";
  }

  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return value;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(parsed);
}

function statusLabel(status: string) {
  switch (status) {
    case "live":
      return "Live";
    case "snapshot":
      return "Reference-backed";
    case "attention":
      return "Needs attention";
    default:
      return status;
  }
}

export function RefreshStatusStrip({ status, title, subtitle, compact = false }: RefreshStatusStripProps) {
  if (!status) {
    return null;
  }

  return (
    <section className={`refresh-strip${compact ? " compact" : ""}`}>
      <div className="section-header">
        <div>
          <h2>{title}</h2>
          <small>{subtitle}</small>
          <p className="refresh-summary">Last refreshed {formatTimestamp(status.generated_at)}</p>
        </div>
        <span className={`status-pill ${status.overall_status}`}>{statusLabel(status.overall_status)}</span>
      </div>

      <div className={`refresh-grid${compact ? " compact" : ""}`}>
        {status.sources.map((source) => (
          <article key={source.key} className="refresh-card">
            <div className="refresh-card-head">
              <span className={`refresh-source-pill ${source.status}`}>{statusLabel(source.status)}</span>
              <strong>{source.label}</strong>
            </div>
            <p>{source.detail}</p>
            <dl className="refresh-meta">
              <div>
                <dt>Last sync</dt>
                <dd>{formatTimestamp(source.updated_at)}</dd>
              </div>
              <div>
                <dt>Feed</dt>
                <dd>{source.source ?? "Local snapshot"}</dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
    </section>
  );
}
