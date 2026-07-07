-- Cleans daily traffic. Casts date, filters obvious zero-row garbage.
-- Aggregation to monthly grain happens in intermediate/.

with source as (
    select * from {{ source('raw', 'raw_traffic') }}
),

renamed as (
    select
        date as event_date,
        brand_key,
        country,
        device,
        users,
        sessions,
        pageviews
    from source
    where users > 0  -- drop days where nobody visited (usually data-quality artefacts)
)

select * from renamed
