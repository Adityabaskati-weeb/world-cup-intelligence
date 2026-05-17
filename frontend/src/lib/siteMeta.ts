type ThemeMode = "dark" | "light";

type RouteMeta = {
  path: string;
  title: string;
  description: string;
};

const BRAND_NAME = "Matchflow";
const DEFAULT_SITE_URL = "https://matchflow-production.vercel.app";

const routeMeta: Record<string, RouteMeta> = {
  "/": {
    path: "/",
    title: "Football Intelligence for World Cup 2026",
    description:
      "Matchflow is a cinematic football intelligence platform for World Cup 2026, blending tournament pulse, explainable match forecasts, xG storytelling, and penalty-duel reasoning.",
  },
  "/tournament-hub": {
    path: "/tournament-hub",
    title: "Tournament Pulse",
    description:
      "Follow group races, fixture narratives, knockout pressure, and tournament freshness signals through Matchflow's live tournament pulse surface.",
  },
  "/match-center": {
    path: "/match-center",
    title: "Match Center",
    description:
      "Forecast World Cup fixtures with explainable momentum, tactical factors, confidence context, and football-first match reasoning.",
  },
  "/xg-explorer": {
    path: "/xg-explorer",
    title: "xG Explorer",
    description:
      "Study shot quality, finishing patterns, and danger zones through team and player xG storytelling in Matchflow.",
  },
  "/penalty-lab": {
    path: "/penalty-lab",
    title: "Penalty Lab",
    description:
      "Scout pressure penalties with kicker-versus-keeper context, placement tendencies, and tournament-stakes reasoning.",
  },
};

function resolveSiteUrl() {
  const configuredUrl = import.meta.env.VITE_SITE_URL?.trim();
  if (configuredUrl) {
    return configuredUrl.replace(/\/$/, "");
  }
  if (typeof window !== "undefined" && window.location.origin) {
    return window.location.origin;
  }
  return DEFAULT_SITE_URL;
}

function upsertMeta(attribute: "name" | "property", key: string, content: string) {
  const selector = `meta[${attribute}="${key}"]`;
  let element = document.head.querySelector<HTMLMetaElement>(selector);
  if (!element) {
    element = document.createElement("meta");
    element.setAttribute(attribute, key);
    document.head.appendChild(element);
  }
  element.setAttribute("content", content);
}

function upsertLink(rel: string, href: string) {
  let element = document.head.querySelector<HTMLLinkElement>(`link[rel="${rel}"]`);
  if (!element) {
    element = document.createElement("link");
    element.setAttribute("rel", rel);
    document.head.appendChild(element);
  }
  element.setAttribute("href", href);
}

export function applyRouteMeta(pathname: string) {
  const meta = routeMeta[pathname] ?? routeMeta["/"];
  const siteUrl = resolveSiteUrl();
  const pageUrl = meta.path === "/" ? `${siteUrl}/` : `${siteUrl}/#${meta.path}`;
  const title = meta.title === BRAND_NAME ? BRAND_NAME : `${meta.title} | ${BRAND_NAME}`;

  document.title = title;
  document.documentElement.dataset.page = meta.path;

  upsertMeta("name", "description", meta.description);
  upsertMeta("property", "og:title", title);
  upsertMeta("property", "og:description", meta.description);
  upsertMeta("property", "og:url", pageUrl);
  upsertMeta("name", "twitter:title", title);
  upsertMeta("name", "twitter:description", meta.description);
  upsertLink("canonical", pageUrl);
}

export function applyThemeMeta(theme: ThemeMode) {
  upsertMeta("name", "theme-color", theme === "light" ? "#f4efe7" : "#071019");
}
