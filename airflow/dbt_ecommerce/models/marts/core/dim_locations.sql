{{
    config(
        materialized='table',
        unique_key='location_id',
    )
}}

WITH all_locations AS (
    SELECT city, state, country FROM {{ ref('stg_product_views') }}
    UNION
    SELECT city, state, country FROM {{ ref('stg_orders') }}
    UNION
    SELECT city, state, country FROM {{ ref('stg_payments') }}
    UNION
    SELECT city, state, country FROM {{ ref('stg_cart_additions') }}
),
deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY city, state, country ORDER BY city DESC) AS rn
    FROM all_locations
)
SELECT 
    to_hex(MD5(to_utf8(CONCAT(COALESCE(city, ''), '-', COALESCE(state, ''), '-', COALESCE(country, ''))))) AS location_key,
    city,
    state,
    country,
    CURRENT_TIMESTAMP AS dbt_updated_at
FROM deduplicated
WHERE rn = 1