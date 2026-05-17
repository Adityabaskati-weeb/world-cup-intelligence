# World Cup Intelligence 2026

World Cup Intelligence 2026 is a full-stack tournament analytics hub for the men's FIFA World Cup 2026 cycle. It combines a match predictor, xG explorer, penalty lab, and knockout simulator in one config-driven project that can be refreshed for future World Cup years.

The codebase is being maintained as a production-quality AI engineering project inspired by:

- Made With ML for lifecycle structure, reproducibility, and deployment discipline
- LangGraph and CrewAI for durable orchestration and persistent workflow memory
- socceraction for football event normalization methodology
- soccerdata for source-specific ingestion and cache-aware data collection
- MLflow for experiment tracking and artifact lineage

## What is included

- FastAPI backend with tournament, fixtures, standings, prediction, xG, penalty, and simulation endpoints
- React frontend with four connected surfaces:
  - `Tournament Hub`
  - `Match Predictor`
  - `xG Explorer`
  - `Penalty Lab`
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

## Data sources

The implementation is designed around the following sources:

- FIFA tournament pages for versioned reference facts and framing
- `football-data.org` for competition and fixture refreshes
- `martj42/international_results` for historical international results and shootouts
- `StatsBomb Open Data` via `statsbombpy` for shot and penalty event data
- `openfootball/worldcup.json` as a convenient public snapshot source for 2026 fixtures

The checked-in snapshot is intentionally light so the app can run offline. Run the refresh pipeline to pull fuller tournament data.

## Local development

The frontend now has a built-in demo runtime. That means you can open the project with just the React app running, and all four surfaces still work from the checked-in snapshot data:

- `Tournament Hub`
- `Match Predictor`
- `xG Explorer`
- `Penalty Lab`
- `Knockout simulator`

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

- If the backend is running on `127.0.0.1:8000`, Vite proxies `/api` requests to it automatically.
- If the backend is not running, the frontend falls back to the bundled World Cup 2026 demo data and keeps the same core functionality available in-browser.

## Public deployment

### Public demo

The repo now includes a GitHub Pages workflow in [.github/workflows/pages.yml](./.github/workflows/pages.yml). It builds the frontend in demo mode and publishes a public static version of the app.

Expected Pages URL:

- [https://adityabaskati-weeb.github.io/world-cup-intelligence/](https://adityabaskati-weeb.github.io/world-cup-intelligence/)

If the first Pages deployment does not publish automatically, enable **Settings -> Pages -> Build and deployment -> GitHub Actions** for the repository, then rerun the workflow.

### Full-stack deployment

For a live API-backed deployment, keep the frontend static and deploy the Python API separately. The existing [render.yaml](./render.yaml) is set up for the backend service and can be paired with Vercel, Render Static Sites, or another static host for the frontend.

## Pipeline commands

```powershell
python pipelines/refresh_all.py
python pipelines/train_match_model.py
python pipelines/train_xg_model.py
python pipelines/train_penalty_model.py
```

If `FOOTBALL_DATA_API_TOKEN` is present, the refresh pipeline will try live fixture and standings hydration from `football-data.org`.

## Experiment tracking

Training pipelines now log tracked runs through MLflow. By default, the local setup uses a writable runtime directory and chooses the most robust backend for that location: SQLite when a machine-local runtime path is available, and MLflow's file store when the project has to fall back to [.runtime](./.runtime/) inside a synced workspace such as OneDrive.

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
