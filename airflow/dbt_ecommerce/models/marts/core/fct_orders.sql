{{
    config(
        materialized='incremental',
        unique_key='event_id',
        incremental_strategy='append'
    )
}}

WITH orders_base AS (
    SELECT 
        event_id,
        event_timestamp,
        event_date,
        event_type,

        user_id,
        to_hex(MD5(to_utf8(CONCAT(COALESCE(city, ''), '-', COALESCE(state, ''), '-', COALESCE(country, ''))))) AS location_key,
        order_id,
        order_status,
        total_amount,
        payment_method,
        device,
        ingestion_timestamp
    FROM {{ ref('stg_orders') }}

    {% if is_incremental() %}
        WHERE event_timestamp > (select max(event_timestamp) from {{ this }})
    {% endif %}
),
payments_info AS (
    SELECT
        order_id,
        payment_status,
        MAX(event_timestamp) AS payment_timestamp
    FROM {{ ref('stg_payments') }}
    GROUP BY order_id, payment_status
)
SELECT
    o.order_id,
    o.event_id,
    o.event_timestamp as order_timestamp,
    o.event_date as order_date,
    o.event_type,

    o.user_id,
    o.location_key,

    o.total_amount,

    o.order_status,
    o.payment_method,
    p.payment_status,
    p.payment_timestamp,

    o.device,
    o.ingestion_timestamp,
    CURRENT_TIMESTAMP AS dbt_updated_at
FROM orders_base o
LEFT JOIN payments_info p ON o.order_id = p.order_id