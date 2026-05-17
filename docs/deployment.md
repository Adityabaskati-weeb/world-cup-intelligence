# Deployment

`Matchflow` is currently deployed as a split Vercel product:

- `frontend/` on Vercel
- `backend/` on Vercel

The checked-in GitHub Pages workflow is no longer a standalone demo path because the frontend now requires a real backend API. Treat it as a secondary static-host option only when it is pointed at a deployed backend.

## Production topology

### Frontend on Vercel

Use the repository as a monorepo and import `frontend/` as the Vercel project root directory.

Recommended environment variables:

- `VITE_API_BASE_URL=https://your-render-service.onrender.com`
- `VITE_PUBLIC_BASE=/`

Recommended Vercel environment scopes:

- Production: `VITE_API_BASE_URL=https://<render-service>.onrender.com`
- Preview: `VITE_API_BASE_URL=https://<staging-render-service>.onrender.com`

Important notes:

- The frontend includes [frontend/vercel.json](../frontend/vercel.json) with an SPA rewrite so direct navigation to routes such as `/match-center` or `/penalty-lab` resolves correctly.
- Vercel monorepos are configured per project by selecting a root directory during import. For this repo, the correct root directory is `frontend/`.

Official references:

- [Vercel monorepos](https://vercel.com/docs/monorepos)
- [Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite)

### Backend on Vercel

The public production backend is currently deployed from `backend/` as a Vercel Python service. This keeps the frontend and API on one hosting platform while the product remains snapshot-backed or light enough for serverless operation.

Suggested environment variables:

- `WCI_ACTIVE_TOURNAMENT=world_cup_2026`
- `WCI_LOG_LEVEL=INFO`
- `WCI_PROJECT_NAME=Matchflow`
- `FOOTBALL_DATA_API_TOKEN=<secret>`
- `MLFLOW_TRACKING_URI=<secret or managed tracking target>`
- `WCI_USE_DEMO_DATA=false`

Notes:

- The Vercel backend currently works well for the deployed snapshot-backed mode and public API contracts.
- If you need persistent jobs, scheduled refreshes with longer runtimes, or a heavier model-serving path, move the API to Render without changing the frontend contract.

### Optional backend on Render

The repository still includes [render.yaml](../render.yaml) as the Render Blueprint for a longer-running FastAPI service.

Suggested environment variables:

- `WCI_ACTIVE_TOURNAMENT=world_cup_2026`
- `WCI_LOG_LEVEL=INFO`
- `WCI_PROJECT_NAME=Matchflow`
- `WCI_USE_DEMO_DATA=false`
- `FOOTBALL_DATA_API_TOKEN=<secret>`
- `MLFLOW_TRACKING_URI=<secret or managed tracking target>`

Notes:

- The blueprint points Render at `backend/` and uses `/api/health` for application-level health checks.
- `FOOTBALL_DATA_API_TOKEN` and `MLFLOW_TRACKING_URI` are declared with `sync: false` so you can provide them as secrets during Blueprint creation.

Official references:

- [Render Blueprint spec](https://render.com/docs/blueprint-spec)
- [Render health checks](https://render.com/docs/health-checks)

## Deploy checklist

1. Create the Vercel backend project from `backend/` or redeploy the existing public API project.
2. Confirm the backend health endpoint responds at `https://<backend-service>/api/health`.
3. Create the Vercel frontend project from the same Git repository.
4. Set the Vercel root directory to `frontend/`.
5. Set `VITE_API_BASE_URL` in Vercel to the public backend URL.
6. Set `VITE_SITE_URL` in Vercel to the public frontend URL.
7. Deploy and verify route refreshes for `/`, `/match-center`, `/xg-explorer`, and `/penalty-lab`.
8. Verify `GET /api/system/overview` on the backend URL for observability and readiness checks.
9. If the backend needs longer-lived refresh jobs later, promote it to Render and update only `VITE_API_BASE_URL`.

## Post-deploy checks

Validate the backend directly:

```powershell
curl https://<render-service>.onrender.com/api/health
curl https://<render-service>.onrender.com/api/system/overview
```

Validate the frontend:

1. Load the Vercel site on desktop and mobile widths.
2. Confirm each route loads without a full-page error.
3. Confirm the runtime badge, data-backed selectors, prediction surfaces, and simulator render against the live backend.
