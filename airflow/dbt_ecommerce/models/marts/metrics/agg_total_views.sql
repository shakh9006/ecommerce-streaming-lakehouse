{{
    config(
        materialized='table'
    )
}}

SELECT
    COUNT(DISTINCT event_id) AS total_views
FROM {{ ref('fct_product_views') }}