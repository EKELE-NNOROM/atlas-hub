with source as (
    select * from {{ atlas_raw('stripe', 'subscription') }}
),

renamed as (
    select
        id as subscription_id,
        customer_id,
        status as subscription_status,
        {{ cents_to_dollars('plan_amount') }} as plan_amount_usd,
        plan_interval,
        current_period_start::timestamp_ntz as period_start_at,
        current_period_end::timestamp_ntz as period_end_at,
        canceled_at::timestamp_ntz as canceled_at,
        created::timestamp_ntz as created_at,
        _fivetran_synced as loaded_at
    from source
)

select * from renamed
