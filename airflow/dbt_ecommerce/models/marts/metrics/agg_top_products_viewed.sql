{{
    config(
        materialized='table'
    )
}}

WITH product_views AS (
    SELECT
        product_id,
        COUNT(*) as view_count,
        COUNT(DISTINCT user_id) as unique_viewers
    FROM {{ ref('fct_product_views') }}
    GROUP BY product_id
)

SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    pv.view_count,
    pv.unique_viewers
FROM product_views pv
JOIN {{ ref('dim_products') }} p ON pv.product_id = p.product_id
ORDER BY pv.view_count DESC, pv.unique_viewers DESC
LIMIT 5