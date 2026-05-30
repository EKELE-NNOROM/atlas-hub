# Sales Business Requirements

## Business Objectives

1. Real-time visibility into pipeline health and forecast accuracy
2. Standardized win/loss and stage conversion analytics
3. Rep and territory performance benchmarking
4. Integration with Finance for bookings-to-revenue reconciliation

## KPIs

| KPI | Definition | Grain | Source | Target |
|-----|------------|-------|--------|--------|
| **Pipeline Value** | Sum of open opportunity amount (weighted optional) | Snapshot daily | Salesforce | Coverage 3× quota |
| **Win Rate** | Won opportunities ÷ (Won + Lost) | Quarter × Segment | Salesforce | > 28% |
| **ACV** | Average annual contract value of won deals | Quarter | Salesforce, Stripe | Increasing |
| **Sales Cycle** | Days from opp created to closed won | Deal | Salesforce | < 90 days |
| **Quota Attainment** | Bookings ÷ quota | Rep × Quarter | Salesforce | > 85% team avg |
| **Forecast Accuracy** | \|Forecast − Actual\| ÷ Actual | Quarter | Salesforce | < 10% |

## Data Contracts

### `mart_sales__pipeline_snapshot`

```yaml
grain: opportunity_id, snapshot_date
scd_type: Type 2 on opportunity dimension
columns:
  - opportunity_id: string, PK component
  - snapshot_date: date, PK component
  - stage_name: string
  - amount_usd: decimal(18,2)
  - probability_pct: decimal(5,2)
  - weighted_amount_usd: decimal(18,2)
  - is_closed: boolean
  - is_won: boolean
sla: Daily snapshot by 06:00 ET
```

### `mart_sales__win_rate`

Pre-aggregated by segment, region, product line, fiscal quarter.

## Acceptance Criteria

- [ ] Pipeline totals match Salesforce list view within $1K
- [ ] Win rate excludes duplicate opps and test accounts
- [ ] SCD Type 2 captures stage changes with valid_from/valid_to
- [ ] Bookings tie to Finance revenue within defined tolerance
- [ ] Row-level security: reps see own territory only
