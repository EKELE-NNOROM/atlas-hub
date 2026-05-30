# Product Business Requirements

## Business Objectives

1. Measure product engagement and feature adoption across customer base
2. Support retention and expansion analysis tied to usage patterns
3. Enable product-led growth experiments with event-level data
4. Feed ML models for churn prediction and segmentation

## KPIs

| KPI | Definition | Grain | Source | Target |
|-----|------------|-------|--------|--------|
| **DAU** | Distinct users with ≥1 product event | Day | Product events (BQ) | Growth |
| **MAU** | Distinct users in rolling 30 days | Day | Product events | Growth |
| **DAU/MAU** | Stickiness ratio | Day | Computed | > 0.25 |
| **Retention** | % users active in period N who return in N+k | Cohort × Week | Product events | D30 > 40% |
| **Feature Adoption** | % MAU using feature X | Feature × Month | Product events | Feature-specific |
| **Activation Rate** | Users completing onboarding ÷ signups | Week | Product + Stripe | > 60% |

## Data Contracts

### `mart_product__daily_engagement`

```yaml
grain: account_id, activity_date
columns:
  - account_id: string
  - activity_date: date
  - dau: integer
  - event_count: integer
  - sessions: integer
  - features_used: array<string>
sla: T+1 08:00 ET (BigQuery → Snowflake sync)
```

### `mart_product__feature_adoption`

Monthly rollup with adoption_pct = feature_users / account_mau.

## Acceptance Criteria

- [ ] Event schema enforced via contract tests on raw layer
- [ ] Bot/internal traffic excluded via allowlist rules
- [ ] Account linkage to Salesforce account_id ≥ 95% match rate
- [ ] Retention cohorts align with Product analytics tool ±2%
- [ ] High-volume events processed in BigQuery; aggregates in Snowflake
