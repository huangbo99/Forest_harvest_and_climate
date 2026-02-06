from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import duckdb

from .config import FORECASTS_DIR, PLANTS_PATH, RUNS_PATH

app = FastAPI(title="Wind Power Forecast API (Parquet)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def q(sql: str, params=None):
    con = duckdb.connect(database=":memory:")
    try:
        return con.execute(sql, params or []).fetchdf()
    finally:
        con.close()


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/runs")
def list_runs():
    if not RUNS_PATH.exists():
        raise HTTPException(404, "runs.parquet not found")
    df = q("SELECT * FROM read_parquet(?) ORDER BY run_time_utc DESC", [str(RUNS_PATH)])
    return df.to_dict(orient="records")


@app.get("/plants")
def list_plants(
    search: str | None = None,
    country: str | None = None,
    installation_type: str | None = None,
    limit: int = Query(200, ge=1, le=5000),
):
    if not PLANTS_PATH.exists():
        raise HTTPException(404, "plants.parquet not found")

    sql = "SELECT * FROM read_parquet(?) WHERE 1=1"
    params = [str(PLANTS_PATH)]

    if search:
        sql += " AND (lower(name) LIKE ? OR lower(plant_id) LIKE ?)"
        s = f"%{search.lower()}%"
        params += [s, s]
    if country:
        sql += " AND country = ?"
        params.append(country)
    if installation_type:
        sql += " AND installation_type = ?"
        params.append(installation_type)

    sql += " ORDER BY country, name LIMIT ?"
    params.append(limit)

    df = q(sql, params)
    return df.to_dict(orient="records")


@app.get("/plants/{plant_id}")
def get_plant(plant_id: str):
    if not PLANTS_PATH.exists():
        raise HTTPException(404, "plants.parquet not found")

    df = q(
        "SELECT * FROM read_parquet(?) WHERE plant_id = ? LIMIT 1",
        [str(PLANTS_PATH), plant_id],
    )
    if df.empty:
        raise HTTPException(404, "plant not found")
    return df.iloc[0].to_dict()


@app.get("/plants/{plant_id}/forecast")
def get_forecast(plant_id: str, run_time_utc: str):
    # Folder layout: forecasts/run_time=YYYY-MM-DDT00/power_forecast_hourly.parquet
    run_folder = FORECASTS_DIR / f"run_time={run_time_utc}"
    fpath = run_folder / "power_forecast_hourly.parquet"
    if not fpath.exists():
        raise HTTPException(404, f"forecast file not found for run_time={run_time_utc}")

    df = q(
        """
        SELECT *
        FROM read_parquet(?)
        WHERE plant_id = ?
        ORDER BY valid_time_utc
        """,
        [str(fpath), plant_id],
    )
    if df.empty:
        raise HTTPException(404, "no forecast rows for that plant/run")

    # Daily energy summary (MWh) by date
    daily = q(
        """
        SELECT
          date_trunc('day', valid_time_utc) AS day_utc,
          SUM(power_mw) AS energy_mwh
        FROM read_parquet(?)
        WHERE plant_id = ?
        GROUP BY 1
        ORDER BY 1
        """,
        [str(fpath), plant_id],
    )

    return {
        "plant_id": plant_id,
        "run_time_utc": run_time_utc,
        "hourly": df.to_dict(orient="records"),
        "daily": daily.to_dict(orient="records"),
    }
