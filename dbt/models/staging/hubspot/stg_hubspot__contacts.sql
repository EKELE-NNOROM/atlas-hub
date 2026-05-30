with source as (
    select * from {{ source('hubspot', 'contact') }}
),

renamed as (
    select
        id as contact_id,
        property_email as email,
        property_firstname as first_name,
        property_lastname as last_name,
        property_lifecyclestage as lifecycle_stage,
        property_hs_lead_status as lead_status,
        property_createdate::timestamp_ntz as created_at,
        _fivetran_synced as loaded_at
    from source
)

select * from renamed
