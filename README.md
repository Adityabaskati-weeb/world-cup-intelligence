# World Cup Intelligence 2026

World Cup Intelligence 2026 is a full-stack football intelligence platform for the men's FIFA World Cup 2026 cycle. It combines a cinematic tournament hub, explainable match reasoning, xG exploration, penalty-duel scouting, and a knockout simulator in one config-driven project that can be refreshed for future World Cup years.

The codebase is being maintained as a production-quality AI engineering project inspired by:

- Made With ML for lifecycle structure, reproducibility, and deployment discipline
- LangGraph and CrewAI for durable orchestration and persistent workflow memory
- socceraction for football event normalization methodology
- soccerdata for source-specific ingestion and cache-aware data collection
- MLflow for experiment tracking and artifact lineage

## What is included

- FastAPI backend with tournament, fixtures, standings, prediction, xG, penalty, simulation, and system-overview endpoints
- React frontend with four connected surfaces:
  - `Tournament Hub`
  - `Match Predictor`
  - `xG Explorer`
  - `Penalty Lab`
- A football-first product layer that emphasizes tournament pulse, sync-state transparency, explainable momentum, and pressure storytelling instead of generic model scores
- Config-driven tournament and cycle files under `configs/`
- Reference snapshots under `data/snapshots/`
- Pipeline scripts for refreshing source data and training baseline models
- MLflow-backed experiment tracking hooks for training pipelines
- Durable workflow state and project-memory persistence under `data/metadata/`
- Backend and frontend tests
- GitHub Actions CI for Python and Node checks

## Project layout

```text
world-cup-intelligence/
  backend/
  frontend/
  pipelines/
  configs/
  data/
    metadata/
  notebooks/
  docs/
  .github/workflows/
```

See [docs/architecture.md](./docs/architecture.md) for the modular architecture baseline.
See [docs/models.md](./docs/models.md) for the current ML workflow, evaluation, and reproducibility rules.

## Data sources

The implementation is designed around the following sources:

- FIFA tournament pages for versioned reference facts and framing
- `football-data.org` for competition and fixture refreshes
- `martj42/international_results` for historical international results and shootouts
- `StatsBomb Open Data` via `statsbombpy` for shot and penalty event data
- `openfootball/worldcup.json` as a convenient public snapshot source for 2026 fixtures

The checked-in snapshot is intentionally light so the backend can boot quickly in snapshot-backed mode. Run the refresh pipeline to pull fuller tournament data.

## Local development

The frontend is now a real API client only. That means every visible workflow expects the FastAPI backend to be available, even when the backend itself is serving snapshot-backed tournament data.

### Backend

```powershell
cd backend
python -m pip install -e .[dev]
python -m uvicorn world_cup_intelligence.api.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open [http://127.0.0.1:5173](http://127.0.0.1:5173/#/).

- If the backend is running on `127.0.0.1:8000`, the frontend calls it directly by default.
- If the backend is not running, the frontend now fails explicitly with clear loading and error states instead of silently switching to mock data.

## API highlights

- `GET /api/refresh/status` exposes per-source sync state, timestamps, and operator-attention signals for tournament, fixture, xG, and penalty layers
- `POST /api/predict/match` returns probabilities plus structured factors, momentum framing, and narrative bullets
- `GET /api/system/overview` surfaces runtime mode, model metadata, workflow state, and request telemetry

## Public deployment

### Production path

The intended production setup is:

- `frontend/` on Vercel
- `backend/` on Render

The repo now includes:

- [frontend/vercel.json](./frontend/vercel.json) for SPA routing on Vercel
- [render.yaml](./render.yaml) for the FastAPI backend on Render
- [docs/deployment.md](./docs/deployment.md) with the deployment checklist and environment setup

### Public demo

The GitHub Pages workflow in [.github/workflows/pages.yml](./.github/workflows/pages.yml) should be treated as a secondary static-host path only. It is no longer a standalone snapshot demo because the frontend does not ship a built-in fake backend.

Current demo URL:

- [https://adityabaskati-weeb.github.io/world-cup-intelligence/](https://adityabaskati-weeb.github.io/world-cup-intelligence/)

## Pipeline commands

```powershell
python pipelines/refresh_all.py
python pipelines/train_match_model.py
python pipelines/train_xg_model.py
python pipelines/train_penalty_model.py
```

If `FOOTBALL_DATA_API_TOKEN` is present, the refresh pipeline will try live fixture and standings hydration from `football-data.org`.

## Experiment tracking

Training pipelines now log tracked runs through MLflow. By default, the local setup prefers a SQLite tracking database when the runtime directory is outside the synced repository, and falls back to MLflow's portable local file store when the workspace is locked down. If you want a shared tracking server for team usage, set `MLFLOW_TRACKING_URI` explicitly.

Example:

```powershell
cd backend
python -m pip install -e .[dev]
python ..\pipelines\train_match_model.py
mlflow ui --backend-store-uri sqlite:///C:/path/to/mlflow.db
```

You can override the tracking target with `MLFLOW_TRACKING_URI` and the runtime root with `WCI_RUNTIME_DIR`.

## Environment management

Copy or adapt [.env.example](./.env.example) for local development. The most important runtime settings are:

- `WCI_ACTIVE_TOURNAMENT`
- `WCI_LOG_LEVEL`
- `MLFLOW_TRACKING_URI`
- `SOCCERDATA_DIR`
- `FOOTBALL_DATA_API_TOKEN`

For the frontend, copy or adapt [frontend/.env.example](./frontend/.env.example) and set:

- `VITE_API_BASE_URL`
- `VITE_PUBLIC_BASE`
