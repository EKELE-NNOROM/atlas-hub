# Atlas Hub — Enterprise Revenue Intelligence Platform

Production-grade data platform for a rapidly growing SaaS company. Centralizes analytics across Marketing, Sales, Finance, Product, HR, and Legal with trusted semantic metrics, governance, and cross-cloud analytics.

## Platform Overview

| Layer | Technology | Purpose |
|-------|------------|---------|
| Ingestion | Fivetran, Airflow, Lambda, S3 | SaaS + custom API extraction |
| Warehouse | Snowflake (primary), BigQuery (GCP) | Enterprise analytics + event analytics |
| Transform | dbt + Semantic Layer | ELT, testing, lineage, metrics |
| ML / Advanced | Databricks (Spark) | Segmentation, churn, forecasting |
| CI/CD | GitHub Actions | Validation, testing, deployments |
| Consumption | Semantic API, marts, executive datasets | Self-service + executive reporting |

## Repository Structure

```
atlas-hub/
├── docker/                  # Dockerfiles and compose helpers
├── docker-compose.yml       # Local dev stack
├── docs/                    # Business requirements, architecture, governance, runbooks
├── dbt/                     # ELT transformations + semantic metrics
├── airflow/                 # Orchestration DAGs
├── lambda/                  # Custom API extractors
├── snowflake/               # DDL, RBAC, security policies
├── fivetran/                # Connector configuration reference
├── databricks/              # ML workloads (segmentation, churn, forecast)
├── bigquery/                # GCP-native event analytics
├── semantic-layer/          # Metric definitions + REST API
└── .github/workflows/       # CI/CD pipelines
```

## Quick Start

### Option A: Docker (recommended for local dev)

No Snowflake required for the default mock demo:

```bash
copy .env.example .env          # Windows
# cp .env.example .env          # Mac/Linux

docker compose up -d --build
# Metrics API: http://localhost:8080/docs
```

See [docs/docker/README.md](docs/docker/README.md) for dbt, Airflow, and Snowflake-connected modes.

### Option B: Native install

#### Prerequisites

- Snowflake account with ACCOUNTADMIN (or delegated admin role)
- AWS account (S3, Lambda, MWAA)
- Fivetran account
- Databricks workspace
- GCP project with BigQuery
- dbt >= 1.7, Python >= 3.11

### Bootstrap Snowflake

Run the SQL scripts in `snowflake/` as SYSADMIN:

```bash
# Execute in order:
# snowflake/ddl/01_databases_schemas.sql
# snowflake/rbac/roles_grants.sql
# snowflake/security/masking_rls_audit.sql
```

### Configure Fivetran

Set up connectors per [docs/architecture/fivetran-implementation.md](docs/architecture/fivetran-implementation.md) using the reference config in `fivetran/connectors.yaml`.

### Run dbt

```bash
cd dbt
cp profiles.yml.example ~/.dbt/profiles.yml  # configure credentials
dbt deps
dbt build --target dev
```

### Deploy Airflow DAGs

Sync `airflow/dags/` to your MWAA S3 bucket. See [docs/production-readiness/runbooks/airflow-deployment.md](docs/production-readiness/runbooks/airflow-deployment.md).

## Key Business Metrics

ARR, MRR, Revenue, Gross Margin, CAC, ROAS, Pipeline Value, Win Rate, DAU, MAU, Retention, Feature Adoption, Headcount, Attrition, Time-to-Hire.

## Documentation Index

- [Docker Local Dev](docs/docker/README.md)
- [Business Requirements](docs/business-requirements/README.md)
- [Architecture](docs/architecture/README.md)
- [Data Governance](docs/governance/README.md)
- [Observability](docs/observability/README.md)
- [Production Readiness](docs/production-readiness/README.md)
- [Architecture Decision Records](docs/production-readiness/adrs/)

## License

Proprietary — Internal use only.
