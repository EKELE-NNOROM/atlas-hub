# BigQuery ↔ Snowflake Integration

## Pattern

1. **Ingest**: GA4 → BigQuery (native); SDK → BigQuery streaming insert
2. **Transform (BQ)**: Event-level scans, sessionization, funnel analysis
3. **Aggregate**: `daily_engagement`, `feature_adoption_daily` materialized in BQ
4. **Export**: Scheduled query → GCS Parquet → S3 cross-cloud transfer → Snowflake `RAW_PROD.S3_LANDING`
5. **Consume**: dbt `stg_product__daily_engagement` → marts → semantic layer

## Why BigQuery for Events

| Factor | BigQuery | Snowflake |
|--------|----------|-----------|
| GA4 native export | Yes | Requires Fivetran/ETL |
| Scan 10B+ rows/day | Cost-effective slot/on-demand | Higher compute cost |
| Nested/repeated fields | Native JSON/ARRAY | VARIANT (good but less GA4-native) |
| Finance KPIs | Secondary | Primary |

## Cross-Cloud Transfer

```bash
# Airflow task: export BQ → GCS
bq extract --destination_format=PARQUET \
  'atlas_events_prod.daily_engagement$20260529' \
  gs://atlas-bq-export-prod/daily_engagement/dt=2026-05-29/*.parquet

# GCS → S3 via Storage Transfer Service or aws s3 sync with dual creds
aws s3 sync s3://atlas-xcloud-prod/daily_engagement/ \
  s3://atlas-landing-prod/product_events/dt=2026-05-29/
```

## Snowflake External Access (Alternative)

For ad-hoc cross-cloud queries without full export:

```sql
CREATE EXTERNAL TABLE analytics_prod.ext_bq_engagement
  WITH LOCATION = @gcs_stage/product_events/
  FILE_FORMAT = (TYPE = PARQUET);
```

## Workloads in BigQuery vs Snowflake

| Workload | Platform |
|----------|----------|
| Session replay funnels | BigQuery |
| ARR / MRR / GL reconciliation | Snowflake |
| Real-time event anomaly detection | BigQuery + Dataflow |
| Executive KPI dashboards | Snowflake semantic layer |
| Cohort retention (billions of events) | BigQuery compute → Snowflake aggregates |
