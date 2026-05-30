with source as (
    select * from {{ source('workday', 'worker') }}
),

renamed as (
    select
        worker_id as employee_id,
        email,
        first_name,
        last_name,
        department,
        cost_center,
        job_title,
        employment_status,
        hire_date::date as hire_date,
        termination_date::date as termination_date,
        fte,
        manager_id,
        _fivetran_synced as loaded_at
    from source
)

select * from renamed
