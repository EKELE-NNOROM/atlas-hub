# Capacity Planning

## Growth Assumptions (12-month)

| Dimension | Current | Projected (+12mo) |
|-----------|---------|-------------------|
| ARR | $12M | $25M |
| Salesforce accounts | 5K | 12K |
| Product events/day | 50M | 200M |
| dbt models | 45 | 80 |
| Analyst users | 40 | 75 |
| Fivetran MAR | 2M | 5M |

## Snowflake Sizing

| Warehouse | Current | +12mo Recommendation |
|-----------|---------|----------------------|
| WH_ETL_PROD | Large | Large → X-Large if dbt > 90 min |
| WH_BI_PROD | Medium | Medium (add cluster if queue > 5s p95) |
| Credit budget | 3500/mo | 6000/mo |

**Trigger to scale**: dbt daily run > 120 min OR warehouse queue time p95 > 10s

## BigQuery

- Events table: 200M rows/day → ~73B rows/year
- Storage: ~50 TB/year compressed
- Export aggregate only to Snowflake (~500K rows/day)

## Airflow MWAA

| Metric | Limit | Action |
|--------|-------|--------|
| Concurrent DAG runs | 25 | Split DAGs if saturated |
| Workers | mw1.large | Upgrade to xlarge at 80% CPU |

## Databricks

- Segmentation job: ~15 min @ 8 workers for 12K accounts
- Churn scoring: weekly, scale workers linearly with account count

## Headcount (Data Platform)

| Role | Current FTE | +12mo |
|------|-------------|-------|
| Data Engineers | 4 | 6 |
| Analytics Engineer | 2 | 3 |
| ML Engineer | 1 | 2 |

## Review
Capacity review quarterly aligned with board planning cycle.
