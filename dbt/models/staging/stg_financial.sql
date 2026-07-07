-- Cleans the raw financial export. One row per brand × month × P&L line.
-- No joins, no business rules — those live in intermediate/.

with source as (
    select * from {{ source('raw', 'raw_financial') }}
),

renamed as (
    select
        period,
        brand_key,
        country,
        currency,
        pl_line,
        pl_category,
        amount as amount_local,
        -- Flag the four revenue lines that later feed the RpM / revenue-mix marts.
        pl_line in ('Advertising Revenue', 'Betting Revenue', 'Subscription Revenue', 'Other Revenue')
            as is_revenue_line
    from source
)

select * from renamed
