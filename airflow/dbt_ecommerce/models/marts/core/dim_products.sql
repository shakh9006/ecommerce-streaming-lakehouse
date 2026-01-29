{{
    config(
        materialized='table',
        unique_key='product_id',
    )
}}

WITH all_products AS (
    SELECT 
        product_id,
        product_name,
        category,
        brand
    FROM {{ ref('stg_product_views') }}

    UNION

    SELECT
        product_id,
        product_name,
        category,
        brand
    FROM {{ ref('stg_cart_additions') }}

    UNION

    SELECT
        product_id,
        product_name,
        category,
        brand
    FROM {{ ref('stg_order_items') }}
),

deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY product_name, category, brand) AS rn
    FROM all_products
)

SELECT 
    product_id,
    product_name,
    category,
    brand,
    CURRENT_TIMESTAMP AS dbt_updated_at
FROM deduplicated
WHERE rn = 1