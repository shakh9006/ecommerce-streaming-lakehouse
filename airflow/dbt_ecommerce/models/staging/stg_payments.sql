{{
    config(
        materialized='incremental',
        unique_key='event_id',
        incremental_strategy='append',
    )
}}

WITH source AS (
    SELECT *
    FROM {{ source('raw', 'events') }}
    WHERE event_type IN ('payment_completed', 'payment_failed')

    {% if is_incremental() %}
        AND event_timestamp > (select max(event_timestamp) from {{ this }})
    {% endif %}
),
parsed AS (
    SELECT
        event_id,
        event_type,
        event_timestamp,
        event_date,
        user_id,
        username,
        session_id,
        device,
        
        location.city AS city,
        location.state AS state,
        location.country AS country,
        
        json_extract_scalar(event_data, '$.transaction_id') AS transaction_id,
        json_extract_scalar(event_data, '$.order_id') AS order_id,
        json_extract_scalar(event_data, '$.payment_method') AS payment_method,
        CASE 
            WHEN event_type = 'payment_completed' THEN 'success'
            WHEN event_type = 'payment_failed' THEN 'failed'
        END AS payment_status,
        
        ingestion_timestamp,
        CURRENT_TIMESTAMP AS dbt_updated_at
    FROM source
),
deduplicated AS (
    SELECT
        event_id,
        event_type,
        event_timestamp,
        event_date,
        user_id,
        username,
        session_id,
        device,
        city,
        state,
        country,
        transaction_id,
        order_id,
        payment_method,
        payment_status,
        ingestion_timestamp,
        dbt_updated_at,
        ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY ingestion_timestamp DESC) AS rn
    FROM parsed
)

SELECT 
    event_id,
    event_type,
    event_timestamp,
    event_date,
    user_id,
    username,
    session_id,
    device,
    city,
    state,
    country,
    transaction_id,
    order_id,
    payment_method,
    payment_status,
    ingestion_timestamp,
    dbt_updated_at
FROM deduplicated
WHERE rn = 1