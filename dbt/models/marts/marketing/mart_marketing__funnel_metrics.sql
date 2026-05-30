with contacts as (
    select * from {{ ref('stg_hubspot__contacts') }}
),

monthly as (
    select
        date_trunc('month', created_at)::date as activity_month,
        count(*) as mql_count,
        count(case when lifecycle_stage = 'marketingqualifiedlead' then 1 end) as mql_qualified_count
    from contacts
    group by 1
),

spend as (
    -- Placeholder: join to ad spend staging when GA/Fivetran campaign cost available
    select
        activity_month,
        0::decimal(18, 2) as marketing_spend_usd
    from monthly
)

select
    m.activity_month,
    m.mql_count,
    s.marketing_spend_usd,
    case
        when m.mql_count > 0 then s.marketing_spend_usd / m.mql_count
        else null
    end as cost_per_mql_usd
from monthly m
left join spend s on m.activity_month = s.activity_month
