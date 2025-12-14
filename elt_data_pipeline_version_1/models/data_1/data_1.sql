
{{ config(materialized='table') }}

SELECT 
    *,
    -- This adds a timestamp column to every row
    CURRENT_TIMESTAMP as loaded_at_utc
FROM read_parquet('s3://latest_ev_data.parquet')