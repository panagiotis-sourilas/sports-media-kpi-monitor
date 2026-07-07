-- One row per brand per month. This is the star of the show — the report
-- renders directly from this table, one query, no post-processing.
--
-- KPIs surfaced:
--   revenue_chf, budget_revenue_chf, revenue_variance_pct
--   ebit_chf, budget_ebit_chf, ebit_variance_pct
--   betting_revenue_chf, betting_share
--   users, sessions, pageviews

with fin as (
    select * from {{ ref('int_financial_vs_budget') }}
),

traffic as (
    select * from {{ ref('int_traffic_vs_target') }}
),

-- Aggregate revenue lines by (brand, period)
revenue as (
    select
        period,
        brand_key,
        country,
        sum(amount_chf)  as revenue_chf,
        sum(budget_chf)  as budget_revenue_chf,
        sum(case when pl_line = 'Betting Revenue' then amount_chf end) as betting_revenue_chf,
        sum(case when pl_line = 'Advertising Revenue' then amount_chf end) as advertising_revenue_chf,
        sum(case when pl_line = 'Subscription Revenue' then amount_chf end) as subscription_revenue_chf,
        sum(case when pl_line = 'Other Revenue' then amount_chf end) as other_revenue_chf
    from fin
    where pl_category = 'Revenue'
    group by 1, 2, 3
),

-- Aggregate costs by (brand, period)
costs as (
    select
        period,
        brand_key,
        sum(amount_chf) as costs_chf,
        sum(budget_chf) as budget_costs_chf
    from fin
    where pl_category = 'Costs'
    group by 1, 2
),

-- Join revenue + costs + traffic
final as (
    select
        r.period,
        r.brand_key,
        r.country,

        -- Financials
        r.revenue_chf,
        r.budget_revenue_chf,
        safe_divide(r.revenue_chf - r.budget_revenue_chf, r.budget_revenue_chf) as revenue_variance_pct,

        c.costs_chf,
        c.budget_costs_chf,

        r.revenue_chf + c.costs_chf as ebit_chf,       -- costs are already negative
        r.budget_revenue_chf + c.budget_costs_chf as budget_ebit_chf,
        safe_divide(
            (r.revenue_chf + c.costs_chf) - (r.budget_revenue_chf + c.budget_costs_chf),
            abs(r.budget_revenue_chf + c.budget_costs_chf)
        ) as ebit_variance_pct,

        -- Revenue mix
        r.betting_revenue_chf,
        r.advertising_revenue_chf,
        r.subscription_revenue_chf,
        r.other_revenue_chf,
        safe_divide(r.betting_revenue_chf, r.revenue_chf) as betting_share,

        -- Traffic (actuals)
        t.users_max_daily as users,
        t.sessions_monthly as sessions,
        t.pageviews_monthly as pageviews,

        -- Traffic targets + variances
        t.users_budget,
        t.users_fc1,
        t.pageviews_budget,
        t.pageviews_fc1,
        t.users_variance_vs_budget,
        t.users_variance_vs_fc1,
        t.pageviews_variance_vs_budget,
        t.pageviews_variance_vs_fc1

    from revenue r
    left join costs c
      on c.period = r.period
     and c.brand_key = r.brand_key
    left join traffic t
      on t.period = r.period
     and t.brand_key = r.brand_key
)

select * from final
