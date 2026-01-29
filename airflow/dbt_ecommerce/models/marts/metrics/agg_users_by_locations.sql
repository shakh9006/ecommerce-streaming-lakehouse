{{
    config(
        materialized='table'
    )
}}


WITH base AS (
    SELECT
        location_key,
        COUNT(DISTINCT order_id) as user_orders
    FROM {{ ref('fct_orders') }}
    GROUP BY location_key
),
orders_count AS (
    SELECT
        COUNT(DISTINCT order_id) as total_orders
    FROM {{ ref('fct_orders') }}
)
SELECT
    l.country,
    l.city,
    ROUND(b.user_orders * 100.0 / (SELECT total_orders FROM orders_count), 2) AS percent_of_total
FROM base b
INNER JOIN {{ ref('dim_locations') }} l ON b.location_key = l.location_key
ORDER BY percent_of_total DESC
LIMIT 5