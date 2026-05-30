with mrr as (
    select * from {{ ref('int_subscription_mrr') }}
),

spine as (
    select * from {{ ref('int_account_spine') }}
),

date_spine as (
    select date_day as revenue_month
    from {{ ref('dim_date') }}
    where date_day = date_trunc('month', date_day)
      and date_day <= current_date()
),

account_months as (
    select
        s.account_id,
        d.revenue_month,
        sum(m.mrr_usd) as mrr_usd,
        sum(m.mrr_usd) * 12 as arr_usd
    from spine s
    cross join date_spine d
    left join mrr m
        on s.account_id = m.account_id
        and d.revenue_month between date_trunc('month', m.period_start_at)
            and coalesce(m.canceled_at, m.period_end_at)
    group by 1, 2
)

select
    account_id,
    revenue_month,
    coalesce(mrr_usd, 0) as mrr_usd,
    coalesce(arr_usd, 0) as arr_usd
from account_months
where account_id is not null
