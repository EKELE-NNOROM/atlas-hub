with closed as (
    select * from {{ ref('stg_salesforce__opportunities') }}
    where is_closed
),

aggregated as (
    select
        date_trunc('quarter', close_date)::date as fiscal_quarter,
        count(case when is_won then 1 end) as won_count,
        count(case when not is_won then 1 end) as lost_count,
        count(*) as closed_count,
        sum(case when is_won then amount_usd else 0 end) as won_amount_usd
    from closed
    group by 1
)

select
    fiscal_quarter,
    won_count,
    lost_count,
    closed_count,
    won_count / nullif(closed_count, 0) as win_rate,
    won_amount_usd / nullif(won_count, 0) as avg_deal_size_usd
from aggregated
