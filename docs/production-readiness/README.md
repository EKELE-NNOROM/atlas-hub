# Production Readiness

## Documents

| Document | Path |
|----------|------|
| Architecture Decision Records | [adrs/](adrs/) |
| Runbooks | [runbooks/](runbooks/) |
| Disaster Recovery | [disaster-recovery.md](disaster-recovery.md) |
| Incident Response | [incident-response.md](incident-response.md) |
| Cost Optimization | [cost-optimization.md](cost-optimization.md) |
| Capacity Planning | [capacity-planning.md](capacity-planning.md) |
| Onboarding | [onboarding.md](onboarding.md) |

## Launch Checklist

- [ ] Snowflake DDL applied in dev → staging → prod
- [ ] Fivetran connectors syncing all 7 SaaS sources
- [ ] dbt `build` passes in prod with 100% Tier 1 tests
- [ ] Airflow DAGs green for 7 consecutive days
- [ ] Metrics API deployed with auth + load test
- [ ] DR tabletop exercise completed
- [ ] On-call rotation configured in PagerDuty
