-- Cleans the raw budget. Same shape as stg_financial to make budget-to-actual
-- matching in intermediate/ a straight join on the key.

with source as (
    select * from {{ source('raw', 'raw_budget') }}
),

renamed as (
    select
        period,
        brand_key,
        country,
        currency,
        pl_line,
        pl_category,
        amount as budget_local
    from source
)

select * from renamed
