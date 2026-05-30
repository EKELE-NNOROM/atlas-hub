{% macro cents_to_dollars(column_name) %}
    ({{ column_name }} / 100.0)::decimal(18, 2)
{% endmacro %}

{% macro exclude_test_accounts(column_name='account_id') %}
    {{ column_name }} not in (
        {% for id in var('exclude_test_account_ids') %}
            '{{ id }}'{% if not loop.last %}, {% endif %}
        {% endfor %}
    )
{% endmacro %}

{% macro generate_surrogate_key(field_list) %}
    {{ dbt_utils.generate_surrogate_key(field_list) }}
{% endmacro %}
