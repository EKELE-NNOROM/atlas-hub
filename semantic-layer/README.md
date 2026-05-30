# Semantic Layer

Reusable metric definitions for Atlas Hub, aligned with dbt Semantic Layer and exposed via REST API.

## Metric Catalog

| Metric | Domain | Definition |
|--------|--------|------------|
| ARR | Finance | Sum of annualized recurring revenue from active subscriptions |
| MRR | Finance | Sum of monthly recurring revenue |
| Revenue | Finance | GAAP recognized revenue from NetSuite |
| Gross Margin | Finance | (Revenue - COGS) / Revenue |
| CAC | Marketing | S&M spend / new customers |
| ROAS | Marketing | Attributed revenue / ad spend |
| Pipeline Value | Sales | Sum of open opportunity amounts |
| Win Rate | Sales | Won / (Won + Lost) |
| DAU | Product | Distinct daily active users |
| MAU | Product | Distinct users in rolling 30 days |
| Retention | Product | Cohort return rate |
| Feature Adoption | Product | Feature users / MAU |
| Headcount | HR | Active employees |
| Attrition | HR | Terminations / avg headcount |
| Time-to-Hire | HR | Days from req open to offer accept |

## API

```bash
cd semantic-layer/api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
```

### Authentication

JWT from corporate IdP with scopes: `finance`, `sales`, `marketing`, `product`, `hr`, `executive`, `admin`.

### Example

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://metrics.internal.company.com/metrics/arr?grain=month
```

## Consumers

- Executive dashboard (`examples/executive_dashboard_consumer.py`)
- Internal PLG application
- Finance close automation

Definitions live in `dbt/models/semantic/_semantic_models.yml`.
