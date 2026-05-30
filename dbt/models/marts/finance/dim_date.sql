with date_spine as (
    select
        date_day,
        date_trunc('month', date_day)::date as month_start,
        date_trunc('quarter', date_day)::date as quarter_start,
        fiscal_year,
        fiscal_quarter,
        is_fiscal_year_end
    from (
        select
            dateadd(day, seq4(), '2018-01-01'::date) as date_day,
            year(dateadd(day, seq4(), '2018-01-01'::date)) as fiscal_year,
            quarter(dateadd(day, seq4(), '2018-01-01'::date)) as fiscal_quarter,
            false as is_fiscal_year_end
        from table(generator(rowcount => 4000))
    )
    where date_day <= dateadd(year, 2, current_date())
)

select * from date_spine
