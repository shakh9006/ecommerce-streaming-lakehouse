{{
    config(
        materialized='incremental',
        unique_key='event_id',
        incremental_strategy='append'
    )
}}

WITH source AS (
    SELECT *
    FROM {{ source('raw', 'events') }}

    {% if is_incremental() %}
        WHERE event_timestamp > (select max(event_timestamp) from {{ this }})
    {% endif %}
),
cleaned AS (
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

        ingestion_timestamp,
        CURRENT_TIMESTAMP AS dbt_updated_at
    FROM source
    WHERE 1=1
        AND event_id IS NOT NULL
        AND event_type IS NOT NULL
        AND event_timestamp IS NOT NULL
        AND event_date IS NOT NULL
        AND user_id IS NOT NULL
        AND username IS NOT NULL
        AND session_id IS NOT NULL
        AND device IS NOT NULL
        AND location.city IS NOT NULL
        AND location.state IS NOT NULL
        AND location.country IS NOT NULL
        AND ingestion_timestamp IS NOT NULL
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
        ingestion_timestamp,
        dbt_updated_at,
        ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY ingestion_timestamp DESC) AS rn
    FROM cleaned
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
    ingestion_timestamp,
    dbt_updated_at
FROM deduplicated
WHERE rn = 1