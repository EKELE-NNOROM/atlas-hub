with source as (
    select * from {{ atlas_raw('stripe', 'customer') }}
),

renamed as (
    select
        id as customer_id,
        email,
        name as customer_name,
        metadata:account_id::string as salesforce_account_id,
        created::timestamp_ntz as created_at,
        _fivetran_synced as loaded_at
    from source
)

select * from renamed
