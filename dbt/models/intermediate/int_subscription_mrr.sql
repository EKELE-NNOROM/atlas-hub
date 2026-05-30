with subscriptions as (
    select * from {{ ref('stg_stripe__subscriptions') }}
),

customers as (
    select * from {{ ref('stg_stripe__customers') }}
),

spine as (
    select * from {{ ref('int_account_spine') }}
),

enriched as (
    select
        s.subscription_id,
        sp.account_id,
        s.customer_id,
        s.subscription_status,
        s.plan_amount_usd,
        s.plan_interval,
        case
            when s.plan_interval = 'month' then s.plan_amount_usd
            when s.plan_interval = 'year' then s.plan_amount_usd / 12.0
            else null
        end as mrr_usd,
        s.period_start_at,
        s.period_end_at,
        s.canceled_at,
        s.created_at
    from subscriptions s
    inner join customers c on s.customer_id = c.customer_id
    left join spine sp on c.salesforce_account_id = sp.account_id
    where s.subscription_status in ('active', 'trialing', 'past_due')
)

select * from enriched
