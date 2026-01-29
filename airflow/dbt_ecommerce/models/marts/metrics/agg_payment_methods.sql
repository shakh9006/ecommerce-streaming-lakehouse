{{
    config(
        materialized='table'
    )
}}

SELECT
    payment_method,
    COUNT(*) as payment_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM {{ ref('fct_payments') }}
WHERE payment_status = 'success'
GROUP BY payment_method
ORDER BY payment_count DESC