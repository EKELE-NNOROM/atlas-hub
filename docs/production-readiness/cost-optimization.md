# Cost Optimization Plan

## Snowflake (Target: 20% reduction YoY at scale)

| Lever | Action | Owner |
|-------|--------|-------|
| Auto-suspend | 60s on BI/adhoc; 120s on ETL | Data Eng |
| Resource monitors | Monthly cap 5000 credits prod; alert 80% | FinOps |
| Warehouse right-sizing | Review query history quarterly | Data Eng |
| Clustering | Cluster large marts on `account_id`, `activity_date` | Data Eng |
| Zero-copy clones | Use for CI/dev instead of full copies | Data Eng |
| Query tagging | Tag dbt/API queries for chargeback | Platform |

## BigQuery

- Require partition filter on events table
- 90-day hot retention; archive older to GCS (Coldline)
- Scheduled queries instead of interactive scans for exports
- BI Engine only if dashboard latency requires

## Databricks

- Job clusters only (no all-purpose prod clusters)
- Autoscale 2–8 workers; spot instances for non-critical jobs
- Delta cache for repeated reads from Snowflake export

## Fivetran

- MAR monitoring; disable unused columns via schema config
- Sync frequency aligned to SLA (not everything hourly)

## AWS

- S3 Intelligent-Tiering for landing zone
- Lambda memory right-sizing via Power Tuning
- MWAA environment class: medium dev, large prod

## Review Cadence
- Weekly: credit burn dashboard
- Monthly: FinOps review with Finance
- Quarterly: architecture cost retrospective
