# Finance Business Requirements

## Business Objectives

1. Single authoritative ARR/MRR/Revenue reporting for board and investors
2. Automated reconciliation between Stripe billing and NetSuite GL
3. Gross margin analysis by product line and customer segment
4. SOX-compliant revenue recognition support data

## KPIs

| KPI | Definition | Grain | Source | Target |
|-----|------------|-------|--------|--------|
| **ARR** | Annualized recurring revenue from active subscriptions | Month × Account | Stripe, Salesforce | Board metric |
| **MRR** | Monthly recurring revenue | Month × Account | Stripe | Board metric |
| **Revenue** | Recognized revenue per GAAP | Month × GL Account | NetSuite | Audit-ready |
| **Gross Margin** | (Revenue − COGS) ÷ Revenue | Month × Product | NetSuite | > 75% |
| **NRR** | Net revenue retention | Cohort × Quarter | Stripe, Salesforce | > 115% |
| **Bookings** | TCV of signed contracts | Month | Salesforce | Plan vs actual |

## Data Contracts

### `mart_finance__monthly_revenue`

```yaml
grain: account_id, revenue_month
columns:
  - account_id: string
  - revenue_month: date  # first of month
  - mrr_usd: decimal(18,2)
  - arr_usd: decimal(18,2)  # mrr * 12 for monthly subs
  - recognized_revenue_usd: decimal(18,2)
  - cogs_usd: decimal(18,2)
  - gross_margin_pct: decimal(8,4)
sla: T+1 06:00 ET (after NetSuite sync)
reconciliation: Stripe MRR vs NetSuite within 0.5%
```

### `mart_finance__reconciliation`

Daily Stripe ↔ NetSuite variance report with exception flags.

## Acceptance Criteria

- [ ] ARR definition documented and versioned in semantic layer
- [ ] Month-end close data locked after Finance approval flag
- [ ] SOX: no manual SQL updates to finance marts in production
- [ ] Audit log captures all access to revenue tables
- [ ] Multi-currency normalized to USD using NetSuite FX rates
