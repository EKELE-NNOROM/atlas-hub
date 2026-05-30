# ADR-001: Snowflake as Primary Enterprise Data Warehouse

## Status
Accepted

## Context
The company requires a centralized analytics platform supporting Finance (SOX), Sales, Marketing, and cross-functional KPIs with strong RBAC, data masking, and separation of storage/compute.

## Decision
Adopt **Snowflake** as the primary EDW on AWS `us-east-1`, with medallion architecture (RAW → ANALYTICS).

## Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **Snowflake** | RBAC/masking, multi-cluster warehouses, Fivetran native | Cost at scale without governance |
| Redshift | AWS-native, lower egress | Weaker masking, more ops |
| BigQuery-only | GCP integration | Finance team on AWS; weaker SOX tooling familiarity |
| Databricks SQL only | Unified with ML | Not ideal as sole financial system of record |

## Consequences
- Positive: Single KPI source, enterprise security features, Fivetran destination
- Negative: Credit costs require resource monitors and warehouse discipline
- BigQuery retained for event analytics only (see ADR-004)

## Tradeoffs
Snowflake prioritizes time-to-trust and governance over lowest raw compute cost.
