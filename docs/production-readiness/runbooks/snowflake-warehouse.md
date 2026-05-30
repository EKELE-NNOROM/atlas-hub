# Runbook: Snowflake Warehouse Saturation

## Symptoms
- Queries queueing (Snowflake query history `queued_overload_time` > 0)
- Credit burn > 20% above daily average
- Reporting consumers report slow query response

## Diagnosis

```sql
SELECT warehouse_name, avg(queued_overload_time) AS avg_queue
FROM snowflake.account_usage.warehouse_load_history
WHERE start_time >= dateadd('hour', -4, current_timestamp())
GROUP BY 1 ORDER BY 2 DESC;
```

## Mitigation

1. **Scale up**: `ALTER WAREHOUSE WH_BI_PROD SET WAREHOUSE_SIZE = 'LARGE';`
2. **Add cluster**: `ALTER WAREHOUSE WH_BI_PROD SET MIN_CLUSTER_COUNT = 1, MAX_CLUSTER_COUNT = 2;`
3. **Kill runaway query**: Identify in query history; cancel if ad-hoc
4. **Route dbt to WH_ETL**: Ensure BI warehouse not used for ETL

## Long-term
- Review query patterns; add clustering keys
- Implement query timeout for ad-hoc role (60 min)
- See [cost-optimization.md](../cost-optimization.md)
