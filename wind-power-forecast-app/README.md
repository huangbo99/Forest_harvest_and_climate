# Wind Power Forecast App (Parquet-first v1)

This scaffold follows your recommended stack:

- **Backend:** FastAPI
- **Data access:** DuckDB over Parquet
- **Frontend:** Next.js (to be initialized in `web/`)

## Project structure

```text
wind-power-forecast-app/
├─ api/
│  ├─ main.py
│  ├─ requirements.txt
│  └─ config.py
├─ web/
│  └─ (Next.js app; initialize in place)
├─ data/
│  ├─ plants/plants.parquet
│  ├─ static_features/plant_static_features.parquet
│  ├─ metadata/runs.parquet
│  └─ forecasts/run_time=.../power_forecast_hourly.parquet
└─ README.md
```

## Local setup

```bash
cd wind-power-forecast-app

# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt

# Frontend (creates files inside web/)
cd web
npx create-next-app@latest . --ts
cd ..
```

## Run backend

```bash
uvicorn api.main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

## Create and push to GitHub

### Option A: with GitHub CLI (`gh`)

```bash
git init
git add .
git commit -m "Initial Parquet-based wind power forecast app scaffold"
gh repo create wind-power-forecast-app --public --source=. --remote=origin --push
```

### Option B: manual remote

1. Create an empty GitHub repository in the browser.
2. Then run:

```bash
git init
git add .
git commit -m "Initial Parquet-based wind power forecast app scaffold"
git branch -M main
git remote add origin https://github.com/<you>/wind-power-forecast-app.git
git push -u origin main
```

## API endpoints

- `GET /health`
- `GET /runs`
- `GET /plants?search=&country=&installation_type=&limit=`
- `GET /plants/{plant_id}`
- `GET /plants/{plant_id}/forecast?run_time_utc=YYYY-MM-DDTHH`
