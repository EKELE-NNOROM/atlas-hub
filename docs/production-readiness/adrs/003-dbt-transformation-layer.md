# ADR-003: dbt for Transformation Layer

## Status
Accepted

## Decision
All business logic from staging through semantic marts implemented in **dbt** with tests, docs, snapshots, and Semantic Layer metrics.

## Alternatives
- Stored procedures in Snowflake: harder to test/version
- Databricks SQL only: splits transformation logic from ML

## Consequences
- Git-versioned transformations with CI (`dbt build` on PR)
- Lineage via `dbt docs generate`
- Snapshots for SCD Type 2 (opportunities)

## Tradeoffs
Complex streaming transforms remain in BigQuery/Databricks; dbt owns batch ELT.
