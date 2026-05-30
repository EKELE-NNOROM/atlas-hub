select
    activity_date,
    dau,
    mau,
    dau_mau_ratio
from {{ ref('mart_product__daily_engagement') }}
