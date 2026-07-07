-- One row per (brand, period, pl_line). Joins actuals to budget.
-- Full outer join because either side can be missing:
--   - actuals row missing = data hasn't loaded yet (should be null, not zero)
--   - budget row missing  = line wasn't budgeted (unusual, still valid)

with actuals as (
    select * from {{ ref('int_financial_chf') }}
),

budget as (
    select * from {{ ref('int_budget_chf') }}
),

joined as (
    select
        coalesce(a.period, b.period)         as period,
        coalesce(a.brand_key, b.brand_key)   as brand_key,
        coalesce(a.country, b.country)       as country,
        coalesce(a.currency, b.currency)     as currency,
        coalesce(a.pl_line, b.pl_line)       as pl_line,
        coalesce(a.pl_category, b.pl_category) as pl_category,
        a.amount_chf,
        b.budget_chf,
        a.amount_chf - b.budget_chf          as variance_chf,
        safe_divide(a.amount_chf - b.budget_chf, b.budget_chf) as variance_pct
    from actuals a
    full outer join budget b
      on a.period = b.period
     and a.brand_key = b.brand_key
     and a.pl_line = b.pl_line
)

select * from joined
