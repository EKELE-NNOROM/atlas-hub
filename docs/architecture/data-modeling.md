# Data modeling reference — Atlas Hub

## Layer Summary

| Layer | Prefix | Example | Materialization |
|-------|--------|---------|-----------------|
| Raw | source tables | `RAW_PROD.STRIPE.SUBSCRIPTION` | Table (Fivetran) |
| Staging | `stg_{source}__{entity}` | `stg_stripe__subscriptions` | View |
| Intermediate | `int_{concept}` | `int_account_spine` | Table |
| Mart | `mart_{domain}__{entity}` | `mart_finance__monthly_revenue` | Table |
| Semantic | `semantic__{domain}_kpis` | `semantic__revenue_kpis` | Table |
| Dimension | `dim_{entity}` | `dim_date` | Table |

## Fact Tables

| Table | Grain | Measures |
|-------|-------|----------|
| `mart_finance__monthly_revenue` | account × month | mrr_usd, arr_usd |
| `mart_sales__pipeline_snapshot` | opportunity × day | amount_usd, weighted_amount_usd |
| `mart_product__daily_engagement` | day | dau, mau |
| `mart_hr__monthly_headcount` | dept × month | headcount, terminations |

## Dimension Tables

| Table | SCD Type | Key |
|-------|----------|-----|
| `dim_date` | N/A | date_day |
| `stg_salesforce__accounts` | Type 1 | account_id |
| `snap_opportunity` | Type 2 | opportunity_id + dbt_valid_from |
| `stg_workday__workers` | Type 2 (via snapshot) | employee_id |

## Slowly Changing Dimensions

- **Opportunities**: dbt snapshot on `loaded_at` — tracks stage/amount history
- **Employees**: Workday daily sync + optional snapshot for department transfers
- **Accounts**: Type 1 for most attributes; segment changes logged in `int_account_history`

## Reusable Metrics (Semantic Layer)

See `dbt/models/semantic/_semantic_models.yml` for full metric catalog.

| Metric | Formula | Domain |
|--------|---------|--------|
| ARR | SUM(arr_usd) | Finance |
| MRR | SUM(mrr_usd) | Finance |
| Pipeline Value | SUM(amount_usd) WHERE open | Sales |
| Win Rate | won / (won + lost) | Sales |
| CAC | marketing_spend / new_customers | Marketing |
| ROAS | attributed_revenue / ad_spend | Marketing |
| DAU / MAU | SUM from product engagement | Product |
| Headcount | Active employees | HR |
| Attrition | terminations / avg_headcount | HR |
