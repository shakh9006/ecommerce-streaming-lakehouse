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
    WHERE event_type = 'order_created'

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

        json_extract_scalar(event_data, '$.order_id') as order_id,
        json_extract_scalar(event_data, '$.order_status') as order_status,
        json_extract_scalar(event_data, '$.total_amount') as total_amount,

        CAST(json_extract(event_data, '$.items') AS VARCHAR) as items_json,

        json_extract_scalar(event_data, '$.payment_method') as payment_method,

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
        order_id,
        order_status,
        total_amount,
        payment_method,
        items_json,
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
    order_id,
    order_status,
    total_amount,
    payment_method,
    items_json,
    ingestion_timestamp,
    dbt_updated_at
FROM deduplicated
WHERE rn = 1