import { useEffect, useState } from "react";
import { NavLink, Route, Routes, useLocation } from "react-router-dom";
import { LandingPage } from "./routes/LandingPage";
import { MatchPredictorPage } from "./routes/MatchPredictorPage";
import { PenaltyLabPage } from "./routes/PenaltyLabPage";
import { TournamentHub } from "./routes/TournamentHub";
import { XgExplorerPage } from "./routes/XgExplorerPage";

type ThemeMode = "dark" | "light";

const links = [
  { to: "/", label: "Home" },
  { to: "/tournament-hub", label: "Tournament Hub" },
  { to: "/match-center", label: "Match Predictor" },
  { to: "/xg-explorer", label: "xG Explorer" },
  { to: "/penalty-lab", label: "Penalty Lab" },
];

function resolveInitialTheme(): ThemeMode {
  if (typeof window === "undefined") {
    return "dark";
  }

  const storedTheme = window.localStorage.getItem("matchflow-theme");
  if (storedTheme === "dark" || storedTheme === "light") {
    return storedTheme;
  }

  if (typeof window.matchMedia === "function" && window.matchMedia("(prefers-color-scheme: light)").matches) {
    return "light";
  }

  return "dark";
}

export default function App() {
  const location = useLocation();
  const isLanding = location.pathname === "/";
  const [theme, setTheme] = useState<ThemeMode>(resolveInitialTheme);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("matchflow-theme", theme);
  }, [theme]);

  return (
    <div className={`app-shell${isLanding ? " app-shell-landing" : ""}`}>
      <header className={`topbar${isLanding ? " topbar-landing" : ""}`}>
        <div className="brand-block">
          <p className="brand-kicker">{isLanding ? "Football intelligence platform" : "Tournament intelligence platform"}</p>
          <p className="brand-title">Matchflow</p>
          <p className="brand-subtitle">
            {isLanding
              ? "A cinematic football intelligence experience for World Cup 2026, built to move from matchday emotion into prediction, xG, and penalty pressure."
              : "Prediction, chance quality, and knockout tension in one football-native decision layer."}
          </p>
        </div>
        <div className="nav-theme-row">
          <nav className="nav-row nav-frame" aria-label="Primary">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) => `nav-chip${isActive ? " active" : ""}`}
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
          <div className="theme-switch" role="group" aria-label="Theme switcher">
            <button
              type="button"
              className={`theme-chip${theme === "dark" ? " active" : ""}`}
              onClick={() => setTheme("dark")}
              aria-pressed={theme === "dark"}
            >
              Dark
            </button>
            <button
              type="button"
              className={`theme-chip${theme === "light" ? " active" : ""}`}
              onClick={() => setTheme("light")}
              aria-pressed={theme === "light"}
            >
              Light
            </button>
          </div>
        </div>
      </header>

      <main className="content-shell">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/tournament-hub" element={<TournamentHub />} />
          <Route path="/match-center" element={<MatchPredictorPage />} />
          <Route path="/xg-explorer" element={<XgExplorerPage />} />
          <Route path="/penalty-lab" element={<PenaltyLabPage />} />
        </Routes>
      </main>
    </div>
  );
}
