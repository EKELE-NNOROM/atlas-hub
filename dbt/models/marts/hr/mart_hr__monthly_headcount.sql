with workers as (
    select * from {{ ref('stg_workday__workers') }}
),

monthly as (
    select
        date_trunc('month', current_date())::date as snapshot_month,
        department,
        count(case when employment_status = 'Active' then 1 end) as headcount,
        count(case when termination_date >= dateadd(month, -1, current_date()) then 1 end) as terminations_last_month,
        avg(datediff(day, hire_date, coalesce(termination_date, current_date()))) as avg_tenure_days
    from workers
    group by 1, 2
)

select * from monthly
