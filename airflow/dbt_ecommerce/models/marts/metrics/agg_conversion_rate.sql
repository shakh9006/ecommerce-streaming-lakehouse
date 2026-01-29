{{
    config(
        materialized='table'
    )
}}

WITH metrics AS (
    SELECT
        (SELECT COUNT(DISTINCT user_id) FROM {{ ref('fct_product_views') }}) as unique_viewers,
        (SELECT COUNT(*) FROM {{ ref('fct_product_views') }}) as total_views,
        
        (SELECT COUNT(DISTINCT user_id) FROM {{ ref('fct_cart_additions') }}) as unique_cart_users,
        (SELECT COUNT(*) FROM {{ ref('fct_cart_additions') }}) as total_cart_additions,
        
        (SELECT COUNT(DISTINCT user_id) FROM {{ ref('fct_orders') }}) as unique_buyers,
        (SELECT COUNT(DISTINCT order_id) FROM {{ ref('fct_orders') }}) as total_orders,
        
        (SELECT COUNT(DISTINCT order_id) 
         FROM {{ ref('fct_orders') }} 
         WHERE payment_status = 'success') as successful_orders
)

SELECT
    unique_viewers,
    total_views,
    unique_cart_users,
    total_cart_additions,
    unique_buyers,
    total_orders,
    successful_orders,
    
    ROUND(unique_cart_users * 100.0 / NULLIF(unique_viewers, 0), 2) as view_to_cart_rate,
    ROUND(unique_buyers * 100.0 / NULLIF(unique_cart_users, 0), 2) as cart_to_order_rate,
    ROUND(unique_buyers * 100.0 / NULLIF(unique_viewers, 0), 2) as overall_conversion_rate,
    ROUND(successful_orders * 100.0 / NULLIF(total_orders, 0), 2) as payment_success_rate,
    
    CURRENT_TIMESTAMP as calculated_at
FROM metrics