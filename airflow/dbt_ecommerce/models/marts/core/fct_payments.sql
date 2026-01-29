{{
    config(
        materialized='incremental',
        unique_key='event_id',
        incremental_strategy='append'
    )
}}

SELECT
    event_id,
    event_timestamp AS payment_timestamp,
    event_date AS payment_date,
    
    user_id,
    to_hex(MD5(to_utf8(CONCAT(COALESCE(city, ''), '-', COALESCE(state, ''), '-', COALESCE(country, ''))))) AS location_key,
    
    transaction_id,
    order_id,
    payment_status,
    payment_method,
    
    session_id,
    device,
    
    ingestion_timestamp,
    CURRENT_TIMESTAMP AS dbt_updated_at
    
FROM {{ ref('stg_payments') }}

{% if is_incremental() %}
WHERE payment_timestamp > (SELECT MAX(payment_timestamp) FROM {{ this }})
{% endif %}