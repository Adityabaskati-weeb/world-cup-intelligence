# World Cup Intelligence 2026

## Summary
- Build a new standalone public GitHub repo named `world-cup-intelligence` for the **men’s FIFA World Cup 2026**, with the first release tailored to the live 2026 tournament cycle.
- Treat the product as a **2026 Tournament Hub** that unifies the three ideas into one experience: `Match Predictor`, `xG Explorer`, `Penalty Lab`, plus a tournament bracket simulator that uses the penalty model to resolve knockout draws.
- Design the app so it refreshes every year for the **World Cup + qualifiers** cycle, while remaining easy to retarget to the next edition by changing tournament config rather than rewriting code.
- Lock current tournament facts into the plan: as of **May 17, 2026**, the tournament runs **June 11, 2026 to July 19, 2026**, has **48 teams**, **12 groups of four**, and a **round of 32** with the top two teams plus the eight best third-placed teams advancing.

## Implementation Changes
- Create the repo as a monorepo with `backend/`, `frontend/`, `pipelines/`, `data/`, `configs/`, `notebooks/`, and `.github/workflows/`.
- Add tournament configuration files such as `configs/tournaments/world_cup_2026.yaml` and `configs/cycles/men_2026.yaml` so the same code can support future editions and yearly qualifier refreshes.
- Build the UI around four connected surfaces: a 2026 home page with groups/fixtures/standings, a match prediction page, a team/player xG analysis page, and a penalty shootout comparison page.
- Add 2026-specific tournament logic for group tables, best-third-place ranking, knockout bracket generation, and host-country handling for Canada, Mexico, and the USA.
- Use FastAPI for the backend and React for the frontend, then deploy React on Vercel and FastAPI on Render.

## Data And Modeling
- Use **FIFA pages** as the source of truth for 2026 schedule/groups/team framing in the product, but keep them as versioned reference snapshots instead of brittle live scraping.
- Use **football-data.org** for programmatic competition, teams, fixtures, standings, and match metadata in the app refresh pipeline.
- Use **martj42/international_results** as the long-history national-team dataset for match outcomes, goal history, neutral-site flags, and historical shootouts.
- Use **StatsBomb Open Data** through **statsbombpy** as the primary event-level source for shots and penalties, centered on World Cup data and expanded with other open competitions only where needed to increase sample size.
- Do **not** use `ClubElo` as the core rating source, because it is club-oriented; instead compute a national-team Elo table in-house from historical international results and optionally show FIFA ranking snapshots as a display feature rather than a hard dependency.
- Match model: train a multinomial or one-vs-rest logistic regression baseline on national-team matches from the recent window, using internal Elo delta, rolling form, rolling goals for/against, neutral-site flag, host/co-host flag, rest days, confederation strength proxy, and tournament-stage features.
- xG model: train an XGBoost classifier on shot events using location, angle, body part, shot type, phase of play, minute, game state, and available contextual event features.
- Penalty Lab: train one model for placement zone and one for conversion probability using kicker footedness, historical direction tendencies, keeper save tendencies, match pressure, tournament context, and shootout order features where available.
- Tournament simulator: use match probabilities for regulation outcomes, then call the penalty model when knockout simulations end level after extra-time assumptions.

## Public Interfaces And Refresh Flow
- `GET /api/tournament/current` returns the active tournament config, dates, groups, host cities, and knockout rules.
- `GET /api/fixtures`, `GET /api/standings`, and `GET /api/groups` power the 2026 hub and yearly qualifier updates.
- `POST /api/predict/match` accepts two teams plus match context and returns home/draw/away probabilities, projected winner, and top drivers.
- `GET /api/xg/team/{team_id}` and `GET /api/xg/player/{player_id}` return shot maps, xG totals, finishing deltas, and zone summaries.
- `POST /api/predict/penalty` accepts a kicker, keeper, and context payload and returns placement probabilities plus expected conversion rate.
- `POST /api/simulate/tournament` simulates group outcomes and the knockout bracket using the current 2026 rules.
- Add scheduled jobs for yearly backfill, post-international-window retraining, daily fixture sync during qualifying windows, and higher-frequency refresh during **June 11, 2026 to July 19, 2026**.

## Test Plan
- Add ingestion tests for each source adapter so schema changes fail fast and source-specific parsing stays isolated.
- Add rules tests for the 2026 format, especially 12-group standings, best-third-place selection, and round-of-32 bracket generation.
- Add feature tests for national-team Elo computation, rolling-form windows, host/co-host indicators, and shootout-history joins.
- Add model smoke tests so all three training pipelines run end-to-end and emit valid probability outputs.
- Add API contract tests for all prediction and tournament endpoints.
- Add frontend tests for group tables, fixture pages, bracket rendering, team/player selectors, and degraded states when live data is unavailable.
- Add one acceptance scenario that simulates a full 2026 knockout path ending in a shootout and verifies the bracket resolves through the penalty model.

## Assumptions And Defaults
- Default scope is the **men’s FIFA World Cup 2026** plus the surrounding qualifier cycle, not women’s tournaments or all competitions.
- First release is a substantial public portfolio project, not a thin MVP.
- PyTorch is deferred from the first implementation unless later experiments clearly outperform the simpler models; the first release should favor reproducibility and shipping speed.
- Future yearly updates should be handled by config, scheduled data refreshes, and retraining, not by cloning the repo for each new tournament.
- Source-backed defaults for implementation:
- FIFA 2026 schedule and dates: [FIFA match schedule](https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/match-schedule-fixtures-results-teams-stadiums)
- FIFA 2026 qualified teams and tournament status: [FIFA qualified teams](https://www.fifa.com/en/articles/world-cup-2026-who-has-qualified?searchOverlay=1)
- Official/open event data structure: [StatsBomb Open Data](https://github.com/statsbomb/open-data)
- Python access to StatsBomb open data: [statsbombpy](https://github.com/statsbomb/statsbombpy)
- Historical international match and shootout data: [martj42/international_results](https://github.com/martj42/international_results)
- Programmatic competition and fixture endpoints: [football-data.org docs](https://www.football-data.org/documentation/quickstart)

Before implementing or modifying anything, always read and analyze the latest version of plan.md and treat it as the primary source of truth for the project requirements, architecture, features, workflows, UI expectations, and deployment goals.

Continuously verify that EVERY feature listed in plan.md is:

* fully implemented
* properly connected
* tested end-to-end
* production-ready
* visually polished
* consistent with the project architecture

At every major step:

1. Re-check plan.md
2. Compare implemented features vs planned features
3. Detect:

   * missing functionality
   * incomplete implementations
   * placeholder code
   * broken integrations
   * UI inconsistencies
   * missing APIs
   * untested workflows
   * poor UX
   * performance bottlenecks
4. Automatically fix and complete them before moving forward.

Never assume a feature is complete without validating:

* frontend behavior
* backend logic
* API integration
* data flow
* model outputs
* error handling
* responsiveness
* loading states
* deployment readiness

The project should NEVER feel like a prototype or hackathon demo. Continuously improve:

* UI/UX quality
* consistency
* responsiveness
* visual hierarchy
* animations/transitions where appropriate
* code organization
* modularity
* naming conventions
* documentation
* maintainability
* scalability

Always make the application look:

* modern
* clean
* professional
* production-grade
* portfolio-worthy

Use engineering best practices inspired by:

* Made With ML
* LangGraph
* CrewAI
* MLflow
* modern SaaS dashboard architecture

Ensure:

* modular folder structure
* reusable components
* typed interfaces where possible
* scalable API design
* proper logging
* environment management
* testing utilities
* clear separation of concerns

For ALL machine learning workflows, strictly follow proper ML engineering and scientific training practices:

* prevent data leakage at every stage
* use separate train, validation, and test datasets correctly
* apply proper feature engineering pipelines
* detect and reduce overfitting and underfitting
* perform hyperparameter tuning systematically
* use cross-validation (K-Fold where appropriate)
* evaluate with meaningful metrics
* compare baseline vs improved models
* validate generalization performance
* maintain reproducibility with fixed seeds/configs
* log experiments and results consistently
* avoid biased or misleading evaluation methods
* monitor class imbalance and feature leakage risks
* ensure inference consistency between training and deployment

Before considering any task complete:

* run tests
* validate all workflows
* verify feature completeness against plan.md
* ensure no partially implemented functionality remains
* improve anything that looks unfinished, inconsistent, or low quality

Persistently maintain awareness of:

* original project vision
* planned roadmap
* architecture decisions
* feature dependencies
* deployment requirements
* UI/UX consistency
  throughout the entire development lifecycle until final completion.
