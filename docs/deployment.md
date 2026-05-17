# Deployment

`World Cup Intelligence 2026` should be deployed as a split-stack product:

- `frontend/` on Vercel
- `backend/` on Render

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

### Backend on Render

The repository includes [render.yaml](../render.yaml) as the Render Blueprint for the FastAPI service.

Suggested environment variables:

- `WCI_ACTIVE_TOURNAMENT=world_cup_2026`
- `WCI_LOG_LEVEL=INFO`
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

1. Create the Render backend service from `render.yaml`.
2. Confirm the backend health endpoint responds at `https://<render-service>/api/health`.
3. Create the Vercel frontend project from the same Git repository.
4. Set the Vercel root directory to `frontend/`.
5. Set `VITE_API_BASE_URL` in Vercel to the public Render backend URL.
6. Deploy and verify route refreshes for `/`, `/match-center`, `/xg-explorer`, and `/penalty-lab`.
7. Verify `GET /api/system/overview` on the Render URL for backend observability and readiness checks.

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
