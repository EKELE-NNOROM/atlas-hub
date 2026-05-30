with accounts as (
    select * from {{ ref('stg_salesforce__accounts') }}
),

stripe_customers as (
    select * from {{ ref('stg_stripe__customers') }}
),

spine as (
    select
        a.account_id,
        a.account_name,
        a.industry,
        a.account_type,
        sc.customer_id as stripe_customer_id,
        a.created_at as account_created_at
    from accounts a
    left join stripe_customers sc
        on a.account_id = sc.salesforce_account_id
)

select * from spine
