# Business Requirements — Atlas Revenue Intelligence Platform

## Executive Summary

Atlas Hub delivers a single source of truth for revenue, customer, and operational KPIs across six stakeholder domains. Requirements are organized by business unit with shared data contracts, SLAs, and acceptance criteria.

## Cross-Functional Objectives

| Objective | Owner | Success Metric |
|-----------|-------|----------------|
| Unified revenue reporting | Finance | < 1% variance vs NetSuite close |
| Pipeline visibility | Sales | Daily refresh by 6 AM ET |
| Marketing ROI | Marketing | ROAS within 5% of ad platform totals |
| Product engagement | Product | DAU/MAU available T+1 |
| Workforce planning | HR | Headcount reconciled to Workday |
| Compliance & audit | Legal | SOX controls + GDPR DSAR < 30 days |

## Global SLAs

| Dataset Tier | Freshness | Availability | Quality |
|--------------|-----------|--------------|---------|
| Tier 1 (Executive) | T+1 by 6 AM ET | 99.9% | 99% test pass |
| Tier 2 (Operational) | T+1 by 8 AM ET | 99.5% | 98% test pass |
| Tier 3 (Exploratory) | T+2 | 99% | 95% test pass |

## Data Contract Standard

Every published mart must include:

```yaml
dataset: mart_finance__monthly_revenue
owner: data-finance@company.com
sla_freshness: "daily by 06:00 America/New_York"
grain: "account_id, revenue_month"
primary_key: ["account_id", "revenue_month"]
schema_version: "1.2.0"
breaking_change_policy: "30-day deprecation notice"
quality_gates:
  - not_null: [account_id, revenue_month, arr_usd]
  - unique: [account_id, revenue_month]
  - accepted_range: { column: arr_usd, min: 0 }
```

## Stakeholder Documents

| Domain | Document | Primary KPIs |
|--------|----------|--------------|
| Marketing | [marketing.md](marketing.md) | CAC, ROAS, MQL→SQL conversion |
| Sales | [sales.md](sales.md) | Pipeline, Win Rate, ACV |
| Finance | [finance.md](finance.md) | ARR, MRR, Revenue, Gross Margin |
| Product | [product.md](product.md) | DAU, MAU, Retention, Feature Adoption |
| HR | [hr.md](hr.md) | Headcount, Attrition, Time-to-Hire |
| Legal | [legal.md](legal.md) | PII inventory, audit trails, DSAR |

## Acceptance Criteria (Platform Launch)

1. All Tier 1 KPIs available in semantic layer with documented definitions
2. End-to-end lineage from source to mart in dbt docs + OpenLineage
3. RBAC enforced: analysts cannot access unmasked PII
4. CI/CD blocks merges on failed dbt tests and SQL validation
5. Runbooks published for top 10 failure modes
6. DR tested: RPO ≤ 4 hours, RTO ≤ 8 hours for Snowflake
