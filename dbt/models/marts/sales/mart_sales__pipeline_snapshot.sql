with opportunities as (
    select * from {{ ref('stg_salesforce__opportunities') }}
),

daily as (
    select
        current_date() as snapshot_date,
        opportunity_id,
        account_id,
        stage_name,
        amount_usd,
        probability_pct,
        amount_usd * (probability_pct / 100.0) as weighted_amount_usd,
        is_closed,
        is_won,
        close_date,
        owner_id
    from opportunities
    where not is_closed
)

select * from daily
