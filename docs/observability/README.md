# Observability — Atlas Hub

## Monitoring Stack

| Layer | Tool | Signals |
|-------|------|---------|
| Ingestion | Fivetran dashboard, CloudWatch | Sync delay, row counts |
| Orchestration | Airflow SLA callbacks, MWAA metrics | DAG duration, failures |
| Transform | dbt Cloud / Elementary | Test failures, freshness |
| Warehouse | Snowflake ACCOUNT_USAGE | Credits, queue time |
| API | Datadog APM | Latency, 5xx, auth failures |
| Incidents | PagerDuty + Slack #data-incidents | On-call routing |

## Data Quality Monitoring

```yaml
# dbt freshness + tests (primary)
# Elementary anomaly detection on row counts (optional package)

alerts:
  - name: arr_freshness_breach
    condition: mart_finance__monthly_revenue loaded_at > 6h stale
    severity: P1
    route: pagerduty-data-platform

  - name: dbt_test_failure
    condition: any tier1 test fail
    severity: P1
    route: pagerduty-data-platform

  - name: fivetran_sync_lag
    condition: sync_delay > 120 min
    severity: P2
    route: slack-data-alerts
```

## SLA Monitoring

| SLA | Measurement | Dashboard Panel |
|-----|-------------|-----------------|
| Tier 1 by 6 AM ET | Airflow `tier1_sla_complete` task timestamp | Executive Data Health |
| dbt test pass rate | `passed / total` daily | Data Quality Scorecard |
| API p99 latency | Datadog trace | Metrics API SLO |

## Alerting Architecture

```
Sources → CloudWatch / Snowflake / dbt / Fivetran
       → EventBridge rules
       → SNS topics (severity-routed)
       → PagerDuty (P1) / Slack (P2-P3)
```

## Logging

- **Airflow**: MWAA task logs → CloudWatch Logs (90 day retention)
- **Lambda**: Structured JSON logs → CloudWatch
- **Metrics API**: JSON access logs → CloudWatch → SIEM
- **Snowflake**: ACCESS_HISTORY → GOVERNANCE_PROD.AUDIT daily export

## Operational Dashboards

1. **Pipeline Health** — DAG success rate, duration trends, SLA hit %
2. **Data Quality** — dbt test results, freshness, anomaly flags
3. **Cost** — Snowflake credits by warehouse, BQ bytes scanned
4. **Consumption** — Semantic API QPS, top metrics, error rate

## Incident Response Workflow

1. Alert fires → PagerDuty ack within 15 min
2. On-call checks [runbook index](../production-readiness/runbooks/README.md)
3. Incident channel in Slack; status page update if Tier 1 breach > 2h
4. Post-incident review within 5 business days (blameless)
5. Action items tracked in Linear/Jira

## Runbook Quick Links

- [dbt failure](../production-readiness/runbooks/dbt-failure.md)
- [Fivetran sync delay](../production-readiness/runbooks/fivetran-sync-delay.md)
- [Snowflake warehouse saturation](../production-readiness/runbooks/snowflake-warehouse.md)
