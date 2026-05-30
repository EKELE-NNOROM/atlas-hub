with engagement as (
    select * from {{ source('product_events', 'daily_engagement') }}
),

daily as (
    select
        activity_date,
        sum(dau) as dau,
        count(distinct account_id) as active_accounts
    from engagement
    group by 1
),

rolling as (
    select
        d.activity_date,
        d.dau,
        d.active_accounts,
        sum(d.dau) over (
            order by d.activity_date
            rows between 29 preceding and current row
        ) as mau_proxy
    from daily d
)

select
    activity_date,
    dau,
    active_accounts,
    mau_proxy as mau,
    dau / nullif(mau_proxy, 0) as dau_mau_ratio
from rolling
