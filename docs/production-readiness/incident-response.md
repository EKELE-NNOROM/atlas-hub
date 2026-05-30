# Incident Response Procedures

## Severity Levels

| Severity | Definition | Response Time | Example |
|----------|------------|---------------|---------|
| P1 | Tier 1 KPIs unavailable or wrong | 15 min ack | ARR mart failed; exec dashboard blank |
| P2 | Tier 2 delayed or degraded | 1 hour | Marketing mart 4h late |
| P3 | Non-critical failure | Next business day | Ad-hoc sandbox issue |

## Response Flow

```
Detect → Triage → Mitigate → Resolve → Post-Mortem
```

1. **Detect**: PagerDuty alert or stakeholder report
2. **Triage**: Identify failing component (ingestion / dbt / API)
3. **Mitigate**: Rollback deploy, skip non-critical models, enable cache
4. **Resolve**: Fix root cause, backfill if needed
5. **Post-Mortem**: Within 5 business days for P1/P2

## Communication Templates

**Initial (within 30 min of P1)**:
> We are investigating delayed availability of executive KPI datasets. ETA update in 60 minutes.

**Resolved**:
> Tier 1 datasets restored as of [time]. Root cause: [brief]. Backfill complete for [dates].

## Escalation

| Step | Contact |
|------|---------|
| L1 | Data Platform on-call |
| L2 | Staff Data Engineer |
| L3 | Principal Data Architect + VP Data |

## Common Playbooks

See [runbooks/](runbooks/) directory.
