# Disaster Recovery Plan — Atlas Hub

## Objectives

| Metric | Target |
|--------|--------|
| RPO (Recovery Point Objective) | 4 hours |
| RTO (Recovery Time Objective) | 8 hours |
| Tier 1 data max staleness during DR | 24 hours |

## Critical Components

| Component | Backup Strategy | Recovery Procedure |
|-----------|-----------------|-------------------|
| Snowflake | Time Travel 90d + Fail-safe 7d; cross-region replication (optional) | Restore tables from Time Travel; re-run dbt |
| S3 Landing | Versioning + cross-region replication | Point Snowpipe to replica bucket |
| Snowflake DDL scripts | Git version control | Re-run scripts from `snowflake/` |
| Airflow MWAA | DAGs in Git; MWAA env via AWS Console/CLI | Recreate MWAA environment; sync DAGs from S3 |
| dbt | Git main branch | `dbt build --full-refresh` if needed |
| Fivetran | Re-sync from source (historical) | Trigger full re-sync per connector |
| BigQuery | GCS export snapshots | Restore from GCS backup |

## DR Scenarios

### Scenario A: Snowflake Region Outage
1. Confirm outage via Snowflake status page
2. Activate comms template (Slack #incidents, exec email)
3. If replication enabled: promote secondary account
4. Else: wait for restoration; replay Fivetran + dbt from last good sync
5. Validate Tier 1 KPIs against last known good export

### Scenario B: Accidental Table Drop
1. `UNDROP TABLE` within Time Travel window
2. If expired: restore from Fail-safe (open Snowflake support case)
3. Re-run downstream dbt models

### Scenario C: AWS us-east-1 Outage
1. MWAA unavailable — manual trigger of Lambda via CLI from backup region
2. Pause non-critical DAGs
3. Semantic API read-only mode from cached Redis if Snowflake reachable

## Testing Schedule
- Quarterly tabletop exercise
- Annual full DR drill (staging environment failover)

## Contacts
- Data Platform On-Call: PagerDuty `data-platform-primary`
- Snowflake Support: Enterprise account TAM
- Fivetran Support: Premium connector support
