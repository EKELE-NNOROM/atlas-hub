-- Gross margin from NetSuite transactions (simplified)
with revenue as (
    select
        date_trunc('month', transaction_date)::date as revenue_month,
        sum(amount) as revenue_usd
    from {{ source('netsuite', 'transaction') }}
    where account_type = 'Income'
    group by 1
),

cogs as (
    select
        date_trunc('month', transaction_date)::date as revenue_month,
        sum(amount) as cogs_usd
    from {{ source('netsuite', 'transaction') }}
    where account_type = 'COGS'
    group by 1
)

select
    r.revenue_month,
    r.revenue_usd,
    coalesce(c.cogs_usd, 0) as cogs_usd,
    r.revenue_usd - coalesce(c.cogs_usd, 0) as gross_profit_usd,
    (r.revenue_usd - coalesce(c.cogs_usd, 0)) / nullif(r.revenue_usd, 0) as gross_margin_pct
from revenue r
left join cogs c on r.revenue_month = c.revenue_month
