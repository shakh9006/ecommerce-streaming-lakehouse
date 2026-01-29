{{
    config(
        materialized='table'
    )
}}

SELECT
    ROUND(SUM(CAST(total_amount AS DOUBLE)), 2) AS total_sales
FROM {{ ref('fct_orders') }}
WHERE payment_status = 'success'