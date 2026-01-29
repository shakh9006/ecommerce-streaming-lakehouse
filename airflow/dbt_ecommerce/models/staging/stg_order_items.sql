{{
    config(
        materialized='incremental',
        unique_key='order_item_id',
        incremental_strategy='append',
    )
}}

WITH orders AS (
    SELECT 
        order_id,
        items_json,
        event_timestamp,
        user_id
    FROM {{ ref('stg_orders') }}

    {% if is_incremental() %}
        WHERE event_timestamp > (select max(event_timestamp) from {{ this }})
    {% endif %}
),
unnested_items AS (
    SELECT
        order_id,
        event_timestamp,
        user_id,

        json_extract_scalar(item, '$.product_id') as product_id,
        json_extract_scalar(item, '$.product_name') as product_name,
        json_extract_scalar(item, '$.category') as category,
        json_extract_scalar(item, '$.brand') as brand,

        CAST(json_extract_scalar(item, '$.price') AS DECIMAL(10, 2)) as price,
        CAST(json_extract_scalar(item, '$.quantity') AS INTEGER) as quantity,
        CAST(json_extract_scalar(item, '$.subtotal') AS DECIMAL(10, 2)) as subtotal,
        
        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY json_extract_scalar(item, '$.product_id')) AS line_number
    FROM orders
    CROSS JOIN UNNEST(CAST(json_parse(items_json) AS ARRAY(JSON))) AS t(item)
)
SELECT
    to_hex(MD5(to_utf8(CONCAT(order_id, '-', product_id, '-', CAST(line_number AS VARCHAR))))) AS order_item_id,

    order_id,
    product_id,
    product_name,
    category,
    brand,
    price,
    quantity,
    subtotal,
    line_number,
    user_id,
    event_timestamp,
    CURRENT_TIMESTAMP AS dbt_updated_at
FROM unnested_items