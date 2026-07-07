-- Budget converted to CHF using the same FX seed as actuals.
-- Same rate for both actual and budget in a given (period, currency) —
-- guarantees variance = amount_chf - budget_chf isn't polluted by FX moves.

with budget as (
    select * from {{ ref('stg_budget') }}
),

fx as (
    select * from {{ ref('fx_rates') }}
),

joined as (
    select
        b.period,
        b.brand_key,
        b.country,
        b.currency,
        b.pl_line,
        b.pl_category,
        b.budget_local,
        fx.rate_to_chf,
        b.budget_local * fx.rate_to_chf as budget_chf
    from budget b
    left join fx
      on fx.period = b.period
     and fx.currency = b.currency
)

select * from joined
