-- Financial actuals converted to CHF using the monthly FX rate.
-- Every downstream KPI reads from this — CHF is the single reporting currency.

with financial as (
    select * from {{ ref('stg_financial') }}
),

fx as (
    select * from {{ ref('fx_rates') }}
),

joined as (
    select
        f.period,
        f.brand_key,
        f.country,
        f.currency,
        f.pl_line,
        f.pl_category,
        f.is_revenue_line,
        f.amount_local,
        fx.rate_to_chf,
        f.amount_local * fx.rate_to_chf as amount_chf
    from financial f
    left join fx
      on fx.period = f.period
     and fx.currency = f.currency
)

select * from joined
