# World Cup Intelligence 2026

World Cup Intelligence 2026 is a full-stack tournament analytics hub for the men's FIFA World Cup 2026 cycle. It combines a match predictor, xG explorer, penalty lab, and knockout simulator in one config-driven project that can be refreshed for future World Cup years.

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
  notebooks/
  .github/workflows/
```

## Data sources

The implementation is designed around the following sources:

- FIFA tournament pages for versioned reference facts and framing
- `football-data.org` for competition and fixture refreshes
- `martj42/international_results` for historical international results and shootouts
- `StatsBomb Open Data` via `statsbombpy` for shot and penalty event data
- `openfootball/worldcup.json` as a convenient public snapshot source for 2026 fixtures

The checked-in snapshot is intentionally light so the app can run offline. Run the refresh pipeline to pull fuller tournament data.

## Local development

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

Set `VITE_API_BASE_URL=http://127.0.0.1:8000` when running the frontend separately.

## Pipeline commands

```powershell
python pipelines/refresh_all.py
python pipelines/train_match_model.py
python pipelines/train_xg_model.py
python pipelines/train_penalty_model.py
```

If `FOOTBALL_DATA_API_TOKEN` is present, the refresh pipeline will try live fixture and standings hydration from `football-data.org`.

