# Docker — Local Development

Run Atlas Hub locally with Docker Compose. No cloud accounts required for the default **mock demo** mode.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) or Docker Engine + Compose v2 (Linux)
- 4 GB RAM available for Docker

## Quick Start (mock mode)

```powershell
# From repo root
copy .env.example .env
docker compose up -d --build
```

Open:

| Service | URL |
|---------|-----|
| Metrics API (Swagger) | http://localhost:8080/docs |
| Health check | http://localhost:8080/health |

Try a metric (auth disabled in mock mode):

```powershell
curl http://localhost:8080/metrics/arr
```

Expected response includes sample ARR data with `"source": "mock"`.

## Compose Profiles

| Profile | Command | What it starts |
|---------|---------|----------------|
| **default** | `docker compose up -d` | Metrics API only |
| **tools** | `docker compose --profile tools run --rm dbt parse` | dbt CLI (one-off) |
| **airflow** | `docker compose --profile airflow up -d` | Airflow + Postgres |
| **localstack** | `docker compose --profile localstack up -d` | S3/Lambda emulator |

## Run dbt in Docker

Configure Snowflake credentials in `.env`, then:

```powershell
docker compose --profile tools run --rm dbt deps
docker compose --profile tools run --rm dbt build --target docker
docker compose --profile tools run --rm dbt test --target docker
```

Interactive dbt shell:

```powershell
docker compose --profile tools run --rm dbt-shell
# inside container:
dbt run --select staging.*
```

## Run Airflow locally

```powershell
docker compose --profile airflow up -d --build
```

| Service | URL | Default login |
|---------|-----|---------------|
| Airflow UI | http://localhost:8081 | admin / admin |

DAGs mount from `airflow/dags/`. The `dbt` project is mounted at `/opt/airflow/dbt` for BashOperator tasks.

> **Note:** Airflow DAGs that invoke AWS Lambda or MWAA-specific connections will need LocalStack or mocked connections for full local runs.

## Connect to real Snowflake

Edit `.env`:

```env
ATLAS_MOCK_DATA=false
ATLAS_DISABLE_AUTH=false
SNOWFLAKE_ACCOUNT=xy12345.us-east-1
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=ANALYTICS_DEV
SNOWFLAKE_WAREHOUSE=WH_ETL_DEV
ATLAS_JWT_SECRET=your-secret
```

For key-pair auth on the Metrics API, place `snowflake_key.p8` in `docker/secrets/` and set:

```env
ATLAS_SNOWFLAKE_PRIVATE_KEY_PATH=/secrets/snowflake_key.p8
```

Generate a dev JWT (when auth enabled):

```powershell
docker compose run --rm metrics-api python /app/../../docker/scripts/generate-dev-token.py
# Or locally:
pip install PyJWT
python docker/scripts/generate-dev-token.py
```

```powershell
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8080/metrics/mrr
```

## LocalStack (optional AWS emulation)

```powershell
docker compose --profile localstack up -d
aws --endpoint-url=http://localhost:4566 s3 mb s3://atlas-landing-dev
```

Useful for testing Lambda extractors and S3 landing patterns without AWS.

## Common Commands

```powershell
# Start / stop
docker compose up -d
docker compose down

# Rebuild after code changes
docker compose up -d --build metrics-api

# View logs
docker compose logs -f metrics-api

# Tear down including volumes
docker compose down -v
```

## Architecture (local)

```
┌─────────────────────────────────────────────────────────┐
│  docker compose                                         │
│  ┌──────────────┐  ┌─────────┐  ┌─────────────────────┐ │
│  │ metrics-api  │  │   dbt   │  │ airflow (optional)  │ │
│  │  :8080       │  │  CLI    │  │  :8081 + postgres   │ │
│  └──────┬───────┘  └────┬────┘  └─────────────────────┘ │
│         │ mock OR       │                             │
│         ▼ Snowflake     ▼ Snowflake                   │
└─────────────────────────────────────────────────────────┘
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 8080 in use | Set `METRICS_API_PORT=8088` in `.env` |
| dbt auth fails | Verify `SNOWFLAKE_*` vars; use password auth in Docker |
| Airflow init loops | `docker compose --profile airflow down -v` then retry |
| Windows line endings | Ensure `.env` uses UTF-8 without BOM |

## What's not in Docker

These remain external cloud services in production:

- **Snowflake** — warehouse (optional for mock mode)
- **Fivetran** — SaaS ingestion
- **Databricks** — ML jobs (run in Databricks workspace)
- **BigQuery** — GCP event analytics

The Docker stack focuses on **local development** of dbt, the Metrics API, and Airflow DAG logic.
