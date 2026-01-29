{{
    config(
        materialized='table'
    )
}}

WITH orders_hourly AS (
    SELECT
        CASE 
            WHEN EXTRACT(HOUR FROM order_timestamp) BETWEEN 0 AND 5 THEN 'Night (00–06)'
            WHEN EXTRACT(HOUR FROM order_timestamp) BETWEEN 6 AND 11 THEN 'Morning (06–12)'
            WHEN EXTRACT(HOUR FROM order_timestamp) BETWEEN 12 AND 17 THEN 'Day (12–18)'
            WHEN EXTRACT(HOUR FROM order_timestamp) BETWEEN 18 AND 23 THEN 'Evening (18–24)'
        END AS order_hour_group,
        order_id,
       total_amount
    FROM {{ ref('fct_orders') }}
    WHERE payment_status = 'success'
)
SELECT
    order_hour_group,
    COUNT(DISTINCT order_id) as order_count,
    ROUND(SUM(CAST(total_amount AS DOUBLE)), 2) as total_revenue
FROM orders_hourly
GROUP BY order_hour_group
ORDER BY order_hour_group DESC