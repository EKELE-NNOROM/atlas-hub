# Fivetran Implementation Guide

## Connector Architecture

All SaaS connectors share:
- **Destination**: Snowflake `RAW_{ENV}.{SOURCE}` schema
- **Sync mode**: Incremental (where supported)
- **Schedule**: Tier 1 sources every 6h; NetSuite/Workday daily

## Sync Schedules (Production)

| Connector | Schedule | Rationale |
|-----------|----------|-----------|
| Salesforce | every_6_hours | Pipeline snapshots |
| Stripe | every_6_hours | MRR freshness |
| HubSpot | every_6_hours | Marketing funnel |
| Zendesk | every_6_hours | Support metrics |
| Google Analytics 4 | daily | GA4 export latency |
| NetSuite | daily | GL close alignment |
| Workday | daily | HR headcount |

## Incremental Loading

- Fivetran uses source-specific CDC (API polling, webhooks)
- `_fivetran_synced` column drives dbt freshness tests
- Soft deletes via `_fivetran_deleted` — filter in staging models

## Schema Evolution

1. **Auto column add**: Enabled; new columns land in RAW
2. **Breaking type change**: Fivetran pauses sync → alert → manual review
3. **dbt update**: Add new columns to staging within 2 business days

## Configuration Management

Connector settings are documented in `fivetran/connectors.yaml` and applied via the **Fivetran UI** or **Fivetran REST API**. OAuth credentials are managed in Fivetran and are not stored in this repository.

## Monitoring & Alerting

- Webhook: sync start/complete/fail → SNS
- CloudWatch metric: `SyncDelayMinutes` (custom Lambda polls Fivetran API)
- dbt source freshness: warn 12h, error 24h
- Weekly MAR review for cost optimization
