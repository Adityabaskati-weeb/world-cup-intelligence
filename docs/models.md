# Model Engineering

Matchflow keeps the three prediction systems aligned around the same engineering rules:

- deterministic seeds
- explicit train, validation, and test splits
- stratified cross-validation for model selection
- leakage inspection before fitting
- MLflow logging for metrics and metadata
- artifact-backed inference so the API and training pipelines stay in sync

## Match Center

- Family: multinomial logistic regression
- Features: Elo delta, form delta, goal-trend delta, rest-days delta, confederation gap, host flag
- Selection: baseline versus tuned model through stratified CV
- Serving artifact: `backend/artifacts/match_model.joblib`

## xG Model

- Family: gradient boosting binary classifier
- Features: distance, angle, minute, pressure, game state, body-part code, shot-type code
- Selection: baseline versus tuned model through stratified CV
- Serving artifact: `backend/artifacts/xg_model.joblib`

## Penalty Lab

- Family: two gradient boosting classifiers
- Placement model predicts target zone
- Conversion model predicts score probability
- Features: pressure, footedness code, keeper bias, match state
- Serving artifact: `backend/artifacts/penalty_model.joblib`

## Experiment Tracking

Each training entrypoint logs:

- split sizes
- CV folds
- best parameters
- ranked CV results
- validation and test metrics
- generalization gaps
- leakage report summaries

## Reproducibility Rules

- Keep `RANDOM_SEED` fixed unless intentionally running a tracked experiment.
- Do not add features that derive from the label or post-event outcomes.
- Retrain artifacts before judging frontend or API prediction changes.
- Use `/api/system/overview` to confirm the currently served model versions and tracked workflow freshness.
