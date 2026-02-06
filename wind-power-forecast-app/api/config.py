from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
PLANTS_PATH = DATA_DIR / "plants" / "plants.parquet"
RUNS_PATH = DATA_DIR / "metadata" / "runs.parquet"
FORECASTS_DIR = DATA_DIR / "forecasts"
