# dbt seeds — sample RAW data without Fivetran

CSV files in this folder mirror **Fivetran/S3 RAW table shapes** so you can run a full **`dbt build`** on Snowflake **without** live connectors.

## When to use seeds

| Scenario | Use seeds? |
|----------|------------|
| CI (`dbt parse`) | No — seeds are optional; parse works without them |
| Mock Metrics API | No — use `ATLAS_MOCK_DATA=true` |
| Snowflake dev, no Fivetran yet | **Yes** |
| Production | **No** — use Fivetran + S3 landing (`use_seeds` defaults to `false`) |

## What's included

| Seed file | Replaces source | Feeds |
|-----------|-----------------|-------|
| `seed_stripe_subscription.csv` | `stripe.subscription` | Finance MRR/ARR |
| `seed_stripe_customer.csv` | `stripe.customer` | Account spine |
| `seed_salesforce_account.csv` | `salesforce.account` | Sales + finance |
| `seed_salesforce_opportunity.csv` | `salesforce.opportunity` | Pipeline, win rate |
| `seed_hubspot_contact.csv` | `hubspot.contact` | Marketing funnel |
| `seed_workday_worker.csv` | `workday.worker` | HR headcount |
| `seed_netsuite_transaction.csv` | `netsuite.transaction` | Gross margin |
| `seed_product_events_daily_engagement.csv` | `product_events.daily_engagement` | DAU/MAU |

## How it works

Staging models call the `atlas_raw()` macro (`macros/atlas_raw.sql`):

- **`use_seeds: false`** (default) → `source()` → RAW Fivetran schemas
- **`use_seeds: true`** → `ref('seed_*')` → tables loaded from these CSVs into `ANALYTICS_{ENV}.SEED`

## Run on Snowflake dev

Prerequisites:

1. Snowflake account with DDL applied (`snowflake/ddl`, `snowflake/rbac`)
2. dbt profile configured (`profiles.yml` or Docker `.env`)
3. Role `ATLAS_TRANSFORMER` on `ANALYTICS_DEV`

```powershell
cd dbt
dbt deps
dbt build --vars "{use_seeds: true}" --target dev
```

`dbt build` runs **seed → models → tests** in order.

Docker:

```powershell
docker compose --profile tools run --rm dbt build --target docker --vars "{use_seeds: true}"
```

## Verify output

After a successful build, check semantic tables (examples):

```sql
SELECT * FROM ANALYTICS_DEV.SEMANTIC.SEMANTIC__REVENUE_KPIS LIMIT 10;
SELECT * FROM ANALYTICS_DEV.MART_SALES.MART_SALES__PIPELINE_SNAPSHOT;
SELECT * FROM ANALYTICS_DEV.MART_PRODUCT.MART_PRODUCT__DAILY_ENGAGEMENT;
```

Then point the Metrics API at Snowflake (`ATLAS_MOCK_DATA=false`) to serve real rows instead of mock JSON.

## Adding rows

1. Edit the CSV (keep Fivetran column names expected by staging SQL).
2. Re-run `dbt seed --vars "{use_seeds: true}"` or full `dbt build`.
3. Avoid IDs in `exclude_test_account_ids` (`dbt_project.yml` vars).

## Switch back to Fivetran

```powershell
dbt build --target dev
```

Omit `use_seeds` or set `use_seeds: false`. Staging reads `RAW_*` sources again.
