# Climains Weather ETL Pipeline

A lightweight weather ETL pipeline that extracts current weather data from the Weatherstack API, transforms it into a normalized dataset, and loads it into a PostgreSQL database. The pipeline is orchestrated with Apache Airflow.

## Features

- Extracts weather data for predefined Nigerian cities
- Transforms API responses into a structured table format
- Loads daily weather records into a PostgreSQL `daily_weather` table
- Runs as a scheduled Airflow DAG (`weather_etl_pipeline`)

## Repository structure

- `pipeline.py` - core ETL functions for extraction, transformation, loading, and data viewing
- `airflow/dags/weather_etl.py` - Airflow DAG definition for scheduling and orchestration
- `airflow/dags/utils.py` - helper module imported by the DAG
- `requirements.txt` - Python dependency list
- `airflow/airflow.cfg` - Airflow configuration file

## Prerequisites

- Python 3.10+ (recommended)
- PostgreSQL database
- `pip` package manager
- `weatherstack` API key

## Install dependencies

1. Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file in the repository root with the following values:

```env
API_KEY=<your_weatherstack_api_key>
DATABASE_URL=postgresql+psycopg2://<user>:<password>@<host>:<port>/<database>
```

Example:

```env
API_KEY=abc123xyz
DATABASE_URL=postgresql+psycopg2://weather_user:password@localhost:5432/climians_db
```

## Airflow setup

1. Set `AIRFLOW_HOME` to the local Airflow directory:

```bash
export AIRFLOW_HOME=$(pwd)/airflow
```

2. Start Airflow in standalone mode:

```bash
airflow standalone
```

3. Open the Airflow UI at `http://localhost:8080` and enable the DAG named `weather_etl_pipeline`.

> If your Airflow instance is already initialized or managed separately, you can skip the local setup above.

## Running the pipeline manually

If you want to run the ETL process without Airflow, you can execute the functions directly from `pipeline.py`:

```bash
python - <<'PY'
from pipeline import extract, transform, load

raw = extract()
transformed_path = transform(raw)
rows = load(transformed_path)
print(f"Loaded rows: {rows}")
PY
```

## DAG details

The Airflow DAG `weather_etl_pipeline` performs the following tasks:

1. `extract` - fetch current weather data from Weatherstack for configured cities
2. `transform` - normalize and flatten the API response into structured records
3. `load` - write the transformed weather data into PostgreSQL
4. `view_database_data` - query and print the loaded `daily_weather` data

## Customization

To change the target cities, update the `LOCATIONS` list in `pipeline.py`.

To modify the database table name or connection behavior, update `pipeline.py` and ensure the `DATABASE_URL` environment variable is correct.

## Notes

- The repository expects the PostgreSQL table to be created automatically by `pandas.DataFrame.to_sql()` when loading data.
- The `transform` step saves intermediate data to `transformed_data.pkl` in the root directory of the project.

## Troubleshooting

- Confirm `API_KEY` and `DATABASE_URL` are set correctly in `.env`
- Ensure the PostgreSQL server is running and accessible
- Check Airflow logs under `airflow/logs/` for DAG task failures

## License

This project does not include a license file. Add one if you want to share or reuse the code publicly.
