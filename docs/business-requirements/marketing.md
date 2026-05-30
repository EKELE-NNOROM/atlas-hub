# Marketing Business Requirements

## Business Objectives

1. Measure campaign ROI and optimize spend allocation across channels
2. Attribute pipeline and revenue to marketing touchpoints
3. Enable self-service funnel analysis for demand gen teams
4. Support board-level marketing efficiency reporting

## KPIs

| KPI | Definition | Grain | Source Systems | Target |
|-----|------------|-------|----------------|--------|
| **CAC** | Total S&M spend ÷ new customers acquired in period | Monthly | HubSpot, Stripe, NetSuite | < $15K |
| **ROAS** | Attributed revenue ÷ ad spend | Campaign × Month | Google Analytics, HubSpot | > 3.0 |
| **MQL Volume** | Count of marketing qualified leads | Daily | HubSpot | Growth QoQ |
| **MQL→SQL Rate** | SQLs ÷ MQLs | Monthly | HubSpot, Salesforce | > 25% |
| **Cost per MQL** | Marketing spend ÷ MQLs | Channel × Month | HubSpot, ad platforms | Decreasing |
| **Pipeline Influenced** | Pipeline $ with marketing attribution | Opportunity × Month | Salesforce, HubSpot | > 60% of pipe |

## Data Contracts

### `mart_marketing__campaign_performance`

```yaml
grain: campaign_id, activity_date
columns:
  - campaign_id: string, not null
  - campaign_name: string
  - channel: string  # paid_search, paid_social, email, organic
  - spend_usd: decimal(18,2)
  - impressions: integer
  - clicks: integer
  - mql_count: integer
  - attributed_pipeline_usd: decimal(18,2)
  - roas: decimal(8,4)  # computed: attributed_revenue / spend
sla: T+1 07:00 ET
```

### `mart_marketing__attribution`

Multi-touch attribution (W-shaped default) linking HubSpot contacts to Salesforce opportunities.

## Acceptance Criteria

- [ ] ROAS reconciles to ±5% vs Google Ads / Meta exports for top 20 campaigns
- [ ] CAC matches Finance definition (shared metric in semantic layer)
- [ ] Campaign dimension includes UTM parameters from GA4
- [ ] Historical data backfilled 24 months
- [ ] PII (email) masked for analyst role; available to marketing_ops role
