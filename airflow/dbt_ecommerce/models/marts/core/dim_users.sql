{{
    config(
        materialized='table',
        unique_key='user_id',
    )
}}

WITH all_users AS (
    SELECT user_id, username FROM {{ ref('stg_product_views') }}
    UNION
    SELECT user_id, username FROM {{ ref('stg_cart_additions') }}
    UNION
    SELECT user_id, username FROM {{ ref('stg_orders') }}
    UNION
    SELECT user_id, username FROM {{ ref('stg_payments') }}
),
deduplicated AS (
    SELECT
        user_id,
        username,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY username) AS rn
    FROM all_users
)
SELECT 
    user_id,
    username,
    CURRENT_TIMESTAMP AS dbt_updated_at
FROM deduplicated
WHERE rn = 1