# ADR-005: Databricks for ML and Advanced Compute

## Status
Accepted

## Decision
**Databricks on AWS** runs customer segmentation, churn prediction, and revenue forecasting. Results write back to Snowflake marts.

## Rationale
Spark for feature engineering at scale, MLflow for model registry, separation from dbt SQL maintenance.

## Not in dbt/Snowflake SQL
- K-Means segmentation (5 clusters)
- GBT churn classifier
- Time-series forecast with custom smoothing / Prophet UDF

## Tradeoffs
Additional platform cost; mitigated by job clusters (not interactive).
