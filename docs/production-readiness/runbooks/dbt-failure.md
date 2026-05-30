# Runbook: dbt Failure in Production

## Symptoms
- Airflow task `dbt_test` or `dbt_marts` failed
- PagerDuty: `dbt_test_failure`
- Stakeholders report stale KPIs

## Diagnosis

1. Open Airflow log for failed task
2. Identify failing model/test from log output
3. Check Snowflake query history for compile errors vs data issues

```bash
# Reproduce locally
cd dbt && dbt run --select +failing_model --target prod
dbt test --select failing_model
```

## Common Causes

| Cause | Fix |
|-------|-----|
| Upstream Fivetran delay | Wait for sync; re-run DAG |
| Source schema change | Update staging model; hotfix PR |
| Test threshold breach | Validate with domain owner; fix data or adjust test |
| Warehouse timeout | Scale WH_ETL temporarily |

## Mitigation

1. If single non-Tier-1 model: skip via `--exclude` and re-run marts
2. If Tier-1 finance model: escalate P1; do not skip without Finance approval
3. Communicate ETA in `#data-incidents`

## Recovery

1. Merge fix to main
2. Trigger `daily_dbt_transform` manually or wait for next schedule
3. Validate Tier 1 tests pass
4. Confirm Metrics API returns fresh data

## Prevention
- Source freshness tests on all Fivetran sources
- PR CI must pass `dbt build` before merge
