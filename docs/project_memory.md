# Project Memory

Updated: `2026-05-17T00:00:00+00:00`

## Project Goals

- Ship a production-quality World Cup analytics platform, not a notebook prototype.
- Keep match prediction, xG analysis, penalty prediction, and tournament simulation in one API-first product.
- Support yearly tournament refreshes through config-driven pipelines and reproducible runs.

## Architecture Decisions

- Use a modular monorepo with explicit separation across ingestion, training, evaluation, API serving, and frontend visualization.
- Keep the backend API stable even when the frontend runs in demo mode.
- Adopt stateful workflow orchestration and durable project memory for long-running data and modeling tasks.

## Feature Engineering Logic

- Match prediction uses national-team Elo delta, recent form, goal trend, rest-days delta, confederation strength gap, and host flag.
- xG modeling uses shot geometry and contextual event features that can later be normalized through socceraction-style action representations.
- Penalty modeling separates target-zone tendency from conversion probability to support both scouting and shootout simulation.

## Evaluation Methodology

- Every training pipeline must emit versioned artifacts plus tracked metrics for reproducibility.
- Classification models should log accuracy, macro F1, and log loss at minimum, with ROC-AUC for binary tasks where possible.
- Tournament logic changes require deterministic tests around qualification and bracket generation.

## Deployment Requirements

- Frontend demo must be publicly deployable as a static site.
- Backend must remain independently deployable as a web API with health checks and environment-based config.
- Experiments, artifacts, and workflow state must be inspectable after runs.

## Football Analytics Assumptions

- soccerdata-style caching and source-specific adapters are the default pattern for scraping or ingesting football datasets.
- socceraction SPADL or Atomic-SPADL is the target normalization direction for future event-level processing.
- Open datasets can power the public demo, but production refreshes must remain source-aware and reproducible.
