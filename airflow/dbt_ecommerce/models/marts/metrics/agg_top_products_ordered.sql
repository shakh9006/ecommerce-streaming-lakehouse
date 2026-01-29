{{
    config(
        materialized='table'
    )
}}

WITH product_orders AS (
    SELECT
        product_id,
        COUNT(DISTINCT order_id) as order_count,
        SUM(quantity) as total_quantity,
        ROUND(SUM(subtotal), 2) as total_revenue
    FROM {{ ref('fct_order_items') }}
    GROUP BY product_id
)

SELECT
    p.product_name,
    p.category,
    p.brand,
    po.order_count,
    po.total_quantity,
    po.total_revenue
FROM product_orders po
JOIN {{ ref('dim_products') }} p ON po.product_id = p.product_id
ORDER BY po.total_revenue DESC, po.order_count DESC
LIMIT 5