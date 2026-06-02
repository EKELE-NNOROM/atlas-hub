select
    revenue_month as activity_month,
    revenue_usd as revenue,
    cogs_usd as cogs,
    gross_margin_pct
from {{ ref('mart_finance__gross_margin') }}
