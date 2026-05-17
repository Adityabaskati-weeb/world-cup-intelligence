# Architecture

Matchflow is being hardened as a production-oriented ML product rather than a notebook-first demo.

## Engineering principles

- API-first backend and independently deployable frontend.
- Explicit separation of ingestion, preprocessing, training, evaluation, serving, and visualization.
- Reproducible experiment tracking and artifact versioning.
- Config-driven tournament refreshes and environment-based runtime settings.
- Durable workflow state and project memory for long-running AI and data tasks.

## Repository layout

```text
world-cup-intelligence/
  backend/
    src/world_cup_intelligence/
      api/
      core/
      data/
      mlops/
      orchestration/
      schemas/
      services/
    tests/
  frontend/
  pipelines/
  configs/
  data/
    snapshots/
    metadata/
  docs/
```

## Design inspirations

### Made With ML

The project follows the same lifecycle split across design, data, model, tracking, evaluation, serving, and developer utilities:

- https://madewithml.com/courses/mlops/

### LangGraph and CrewAI

We are not forcing heavyweight agent dependencies into every path, but we are adopting their production patterns:

- durable workflow execution
- explicit state transitions
- persistent memory of goals and decisions
- orchestration that can grow into longer-running autonomous data tasks

References:

- https://docs.langchain.com/oss/python/langgraph/overview
- https://docs.crewai.com/en/concepts/flows

### socceraction

Event normalization should evolve toward SPADL or Atomic-SPADL style action tables for consistent football analytics methodology, especially as the xG and possession-value parts mature:

- https://socceraction.readthedocs.io/en/latest/documentation/spadl/spadl.html

### soccerdata

Source-specific ingestion, caching, and environment-managed data directories should remain the default pattern for football scraping and data collection:

- https://soccerdata.readthedocs.io/en/stable/intro.html

### MLflow

All model training is moving under tracked runs with logged parameters, metrics, and artifacts so experiments remain reproducible locally and in team deployments:

- https://mlflow.org/docs/latest/ml/tracking/

## Current workflow boundaries

### Ingestion

- `pipelines/fetch_*`
- `backend/src/world_cup_intelligence/data/adapters.py`

### Training and evaluation

- `backend/src/world_cup_intelligence/services/training.py`
- `backend/src/world_cup_intelligence/mlops/evaluation.py`
- `backend/src/world_cup_intelligence/mlops/tracking.py`

### Orchestration and memory

- `backend/src/world_cup_intelligence/orchestration/workflows.py`
- `backend/src/world_cup_intelligence/orchestration/memory.py`

### Serving

- `backend/src/world_cup_intelligence/api/main.py`

### Visualization

- `frontend/src/routes/`
- `frontend/src/components/`

## Quality bar going forward

- No new feature should land only in a notebook.
- Any new model or dataset path should define config, pipeline entrypoints, evaluation outputs, and serving implications.
- Architecture decisions and football assumptions should be written down in project memory as they evolve.
