select
    snapshot_month as activity_month,
    sum(headcount) as headcount,
    sum(terminations_last_month) as terminations,
    avg(avg_tenure_days) as avg_tenure_days
from {{ ref('mart_hr__monthly_headcount') }}
group by 1
