select
    activity_month,
    marketing_spend_usd as marketing_spend,
    mql_count as new_customers,
    marketing_spend_usd as ad_spend,
    coalesce(marketing_spend_usd * 3, 0)::decimal(18, 2) as attributed_revenue
from {{ ref('mart_marketing__funnel_metrics') }}
