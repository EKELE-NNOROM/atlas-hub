{% snapshot snap_opportunity %}

{{
    config(
      target_schema='INT',
      unique_key='opportunity_id',
      strategy='timestamp',
      updated_at='loaded_at',
      invalidate_hard_deletes=True
    )
}}

select * from {{ ref('stg_salesforce__opportunities') }}

{% endsnapshot %}
