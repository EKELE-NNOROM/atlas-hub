select
    opportunity_id,
    account_id,
    snapshot_date,
    amount_usd,
    weighted_amount_usd,
    stage_name
from {{ ref('mart_sales__pipeline_snapshot') }}
