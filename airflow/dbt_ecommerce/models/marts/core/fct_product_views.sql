{{
    config(
        materialized='incremental',
        unique_key='event_id',
        incremental_strategy='append'
    )
}}

SELECT
    event_id,
    event_timestamp,
    event_date,

    user_id,
    product_id,
    to_hex(MD5(to_utf8(CONCAT(COALESCE(city, ''), '-', COALESCE(state, ''), '-', COALESCE(country, ''))))) AS location_key,

    device,
    ingestion_timestamp,
    CURRENT_TIMESTAMP AS dbt_updated_at
FROM {{ ref('stg_product_views') }}

{% if is_incremental() %}
    WHERE event_timestamp > (select max(event_timestamp) from {{ this }})
{% endif %}
