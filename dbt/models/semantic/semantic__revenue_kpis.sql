select
    account_id,
    revenue_month,
    mrr_usd,
    arr_usd
from {{ ref('mart_finance__monthly_revenue') }}
