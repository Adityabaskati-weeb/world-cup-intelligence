import type { ReactNode } from "react";

type Tone = "info" | "loading" | "error";

type Props = {
  title: string;
  tone?: Tone;
  children?: ReactNode;
};

export function StatusMessage({ title, tone = "info", children }: Props) {
  return (
    <div
      className={`status-card status-${tone}`}
      role={tone === "error" ? "alert" : "status"}
      aria-live={tone === "error" ? "assertive" : "polite"}
    >
      <strong>{title}</strong>
      {children ? <p>{children}</p> : null}
    </div>
  );
}
