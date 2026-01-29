{{
    config(
        materialized='table'
    )
}}

SELECT
    category,
    COUNT(DISTINCT order_id) as order_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM {{ ref('fct_order_items') }}
GROUP BY category
ORDER BY order_count DESC