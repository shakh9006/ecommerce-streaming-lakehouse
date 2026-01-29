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
    WHERE event_type = 'product_viewed'

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

        json_extract_scalar(event_data, '$.product_id') as product_id,
        json_extract_scalar(event_data, '$.product_name') as product_name,
        json_extract_scalar(event_data, '$.brand') as brand,
        json_extract_scalar(event_data, '$.category') as category,

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
        product_id,
        product_name,
        brand,
        category,
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
    product_id,
    product_name,
    brand,
    category,
    ingestion_timestamp,
    dbt_updated_at
FROM deduplicated
WHERE rn = 1