# ADR-002: Fivetran for SaaS Application Ingestion

## Status
Accepted

## Context
Nine SaaS sources (Salesforce, HubSpot, Stripe, etc.) require reliable incremental sync with schema drift handling.

## Decision
Use **Fivetran** for all supported SaaS connectors into Snowflake RAW schemas. Custom sources use Lambda + Airflow.

## Alternatives Considered
- **Airbyte (self-hosted)**: Lower license cost, higher ops burden
- **Stitch**: Fewer enterprise connectors
- **Custom Airflow only**: Full control but high maintenance for schema changes

## Consequences
- Managed sync SLAs and connector maintenance
- Fivetran connector config documented in `fivetran/connectors.yaml`
- Incremental sync via Fivetran `_fivetran_synced`; MERGE handled by vendor

## Schema Evolution Strategy
1. Fivetran auto-adds columns (enabled per connector)
2. dbt sources updated via CI when new columns needed in marts
3. Breaking changes: Fivetran schema change alerts → data eng triage

## Monitoring
- Fivetran webhook → SNS → Slack
- CloudWatch custom metric for sync delay
- dbt source freshness on `_fivetran_synced`
