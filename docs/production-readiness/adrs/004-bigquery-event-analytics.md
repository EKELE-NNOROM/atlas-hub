# ADR-004: BigQuery for High-Volume Event Analytics

## Status
Accepted

## Decision
Product usage events land in **BigQuery** (`atlas_events_prod`); daily aggregates export to Snowflake for unified KPIs.

## Rationale
GA4 native export, cost-effective petabyte scans, JSON-native event params.

## Tradeoffs
Cross-cloud transfer adds latency (T+1 acceptable for DAU/MAU); not used for financial reporting.
