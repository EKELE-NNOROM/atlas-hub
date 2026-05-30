# Runbooks Index

| Runbook | When to Use |
|---------|-------------|
| [dbt-failure.md](dbt-failure.md) | dbt test or run failure in prod DAG |
| [fivetran-sync-delay.md](fivetran-sync-delay.md) | Fivetran connector > 2h behind |
| [snowflake-warehouse.md](snowflake-warehouse.md) | Query queueing, credit spike |
| [airflow-deployment.md](airflow-deployment.md) | Deploy or rollback DAGs |

## On-Call Checklist (Daily)

1. Check Airflow DAG `daily_dbt_transform` completed before 6 AM ET
2. Review `#data-alerts` Slack for overnight warnings
3. Verify Fivetran dashboard: all connectors green
4. Glance at Snowflake credit burn vs budget
