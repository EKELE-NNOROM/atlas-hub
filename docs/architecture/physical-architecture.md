# Physical Architecture

## Cloud Topology

```mermaid
flowchart TB
    subgraph AWS["AWS (us-east-1)"]
        MWAA[MWAA Airflow]
        S3L[S3 atlas-landing-{env}]
        S3A[S3 atlas-airflow-{env}]
        LMD[Lambda Extractors]
        SM[Secrets Manager]
        CW[CloudWatch]
        SNS[SNS Alerts]
    end

    subgraph Snowflake["Snowflake (AWS us-east-1)"]
        WH_ETL[WH_ETL — L]
        WH_BI[WH_BI — M]
        WH_ADHOC[WH_ADHOC — XS auto-suspend 60s]
        DB_RAW[(RAW_PROD)]
        DB_AN[(ANALYTICS_PROD)]
    end

    subgraph GCP["GCP (us-central1)"]
        BQ[(BigQuery atlas_events)]
        GCS[GCS GA4 Export]
    end

    subgraph Databricks["Databricks (AWS)"]
        DBX_WS[Workspace]
        DBX_JOBS[Jobs Cluster]
        UC[Unity Catalog]
    end

    subgraph SaaS["Managed SaaS"]
        FT[Fivetran]
        GHA[GitHub Actions]
    end

    FT --> DB_RAW
    MWAA --> LMD & S3L
    LMD --> S3L --> DB_RAW
    MWAA --> Snowflake
    GCS --> BQ
    BQ -->|Scheduled export| S3L
    DBX_JOBS --> DB_AN
    GHA --> MWAA & Snowflake & TF
    CW --> SNS
```

## Snowflake Database Layout

| Database | Schemas | Retention |
|----------|---------|-----------|
| `RAW_{ENV}` | `SALESFORCE`, `HUBSPOT`, `STRIPE`, `NETSUITE`, `WORKDAY`, `ZENDESK`, `S3_LANDING` | 7 years |
| `ANALYTICS_{ENV}` | `STG_*`, `INT`, `MART_FINANCE`, `MART_SALES`, `MART_MARKETING`, `MART_PRODUCT`, `MART_HR`, `SEMANTIC` | Indefinite (marts) |
| `GOVERNANCE_{ENV}` | `AUDIT`, `LINEAGE`, `QUALITY` | 7 years |

## Warehouse Sizing

| Warehouse | Size | Workload | Auto-Suspend |
|-----------|------|----------|--------------|
| `WH_ETL_{ENV}` | Large | dbt runs, Snowpipe | 120s |
| `WH_BI_{ENV}` | Medium | BI queries | 60s |
| `WH_ADHOC_{ENV}` | X-Small | Analyst sandbox | 60s |
| `WH_ML_{ENV}` | Medium | Databricks write-back | 120s |

## Network & Security

- Snowflake: PrivateLink to AWS VPC (MWAA, Lambda in same VPC)
- Secrets: AWS Secrets Manager → Airflow connections / Lambda env
- No public Snowflake URLs; SSO via Okta
- S3 buckets: SSE-KMS, block public access, lifecycle to Glacier after 365 days

## High Availability

- Snowflake: Multi-AZ by platform; Time Travel 90 days prod
- MWAA: AWS-managed HA (2 schedulers, multi-AZ workers)
- Fivetran: Vendor SLA 99.9%; destination failover documented in DR plan

## Cost Controls

- Resource monitors on all warehouses (monthly credit cap + alert at 80%)
- Auto-suspend on all non-ETL warehouses
- BigQuery: partitioned + clustered event tables; 90-day hot, archive to GCS
- Databricks: job clusters (not all-purpose) with autoscaling 2–8 workers
