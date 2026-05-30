with source as (
    select * from {{ source('salesforce', 'opportunity') }}
),

renamed as (
    select
        id as opportunity_id,
        account_id,
        name as opportunity_name,
        stage_name,
        amount as amount_usd,
        probability as probability_pct,
        is_closed,
        is_won,
        close_date,
        created_date::timestamp_ntz as created_at,
        owner_id,
        type as opportunity_type,
        lead_source,
        _fivetran_synced as loaded_at
    from source
    where not coalesce(is_deleted, false)
)

select * from renamed
