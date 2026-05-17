import { NavLink, Route, Routes } from "react-router-dom";
import { MatchPredictorPage } from "./routes/MatchPredictorPage";
import { PenaltyLabPage } from "./routes/PenaltyLabPage";
import { TournamentHub } from "./routes/TournamentHub";
import { XgExplorerPage } from "./routes/XgExplorerPage";

const links = [
  { to: "/", label: "Tournament Hub" },
  { to: "/match-center", label: "Match Predictor" },
  { to: "/xg-explorer", label: "xG Explorer" },
  { to: "/penalty-lab", label: "Penalty Lab" },
];

export default function App() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="brand-kicker">Analytics platform</p>
          <h1 className="brand-title">World Cup Intelligence 2026</h1>
        </div>
        <nav className="nav-row">
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
      </header>

      <main className="content-shell">
        <Routes>
          <Route path="/" element={<TournamentHub />} />
          <Route path="/match-center" element={<MatchPredictorPage />} />
          <Route path="/xg-explorer" element={<XgExplorerPage />} />
          <Route path="/penalty-lab" element={<PenaltyLabPage />} />
        </Routes>
      </main>
    </div>
  );
}

