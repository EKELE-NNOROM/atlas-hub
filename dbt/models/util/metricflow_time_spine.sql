{{ config(materialized='view', tags=['semantic', 'utility']) }}

with spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2018-01-01' as date)",
        end_date="cast('2030-12-31' as date)"
    ) }}
)

select date_day
from spine
