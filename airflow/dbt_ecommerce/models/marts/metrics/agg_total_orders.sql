{{
    config(
        materialized='table'
    )
}}

SELECT
    COUNT(DISTINCT order_id) AS total_orders
FROM {{ ref('fct_orders') }}