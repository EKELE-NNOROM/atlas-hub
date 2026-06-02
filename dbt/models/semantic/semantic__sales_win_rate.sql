select
    fiscal_quarter,
    win_rate
from {{ ref('mart_sales__win_rate') }}
