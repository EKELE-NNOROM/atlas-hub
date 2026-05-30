# Runbook: Fivetran Sync Delay

## Symptoms
- dbt source freshness test failure on `_fivetran_synced`
- CloudWatch alarm `fivetran-sync-lag`
- Fivetran dashboard shows delayed connector

## Diagnosis

1. Fivetran UI → Connector → Sync History
2. Check for API rate limits, authentication errors, or warehouse load failures
3. Verify Snowflake destination is accessible

## Resolution Steps

| Error Type | Action |
|------------|--------|
| Auth expired | Re-authenticate connector in Fivetran UI |
| API limit | Pause non-critical connectors; contact vendor |
| Snowflake load fail | Check WH availability; disk space; re-sync |
| Schema drift block | Review schema change; approve in Fivetran |

## Manual Re-sync

1. Fivetran → Connector → Sync Now
2. Monitor until complete
3. Re-trigger Airflow `daily_dbt_transform`

## Escalation
- > 4 hours delay on Stripe or Salesforce → P1 escalate to Fivetran support
