with source as (
    select * from {{ atlas_raw('salesforce', 'account') }}
),

renamed as (
    select
        id as account_id,
        name as account_name,
        industry,
        type as account_type,
        annual_revenue,
        number_of_employees,
        billing_country,
        created_date::timestamp_ntz as created_at,
        last_modified_date::timestamp_ntz as updated_at,
        is_deleted,
        _fivetran_synced as loaded_at
    from source
    where not coalesce(is_deleted, false)
)

select * from renamed
where {{ exclude_test_accounts('account_id') }}
