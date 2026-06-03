{#-
  Resolve a RAW-layer relation for staging models.

  Production (default): Fivetran / S3-loaded tables via `source()`.
  Dev without connectors: CSV seeds via `ref()` when `var('use_seeds')` is true.

  Seed file naming: seeds/seed_{source_name}_{table_name}.csv
  Example: seed_stripe_subscription.csv for source('stripe', 'subscription')
-#}
{% macro atlas_raw(source_name, table_name) %}
    {% if var('use_seeds', false) %}
        {{ return(ref('seed_' ~ source_name ~ '_' ~ table_name)) }}
    {% else %}
        {{ return(source(source_name, table_name)) }}
    {% endif %}
{% endmacro %}
