-- Monthly traffic actuals joined to Budget + FC1 targets.
-- One row per (brand, period). Wide-format targets (users_budget, users_fc1,
-- pageviews_budget, pageviews_fc1) so the mart can compute variances directly.

with traffic as (
    select * from {{ ref('int_traffic_monthly') }}
),

-- Pivot the seed from long (metric, budget, fc1) to wide (users_budget, users_fc1, ...)
targets as (
    select
        brand_key,
        period,
        max(case when metric = 'users'     then budget end) as users_budget,
        max(case when metric = 'users'     then fc1    end) as users_fc1,
        max(case when metric = 'pageviews' then budget end) as pageviews_budget,
        max(case when metric = 'pageviews' then fc1    end) as pageviews_fc1
    from {{ ref('traffic_targets') }}
    group by brand_key, period
)

select
    t.period,
    t.brand_key,
    t.country,
    t.users_max_daily,
    t.sessions_monthly,
    t.pageviews_monthly,
    tgt.users_budget,
    tgt.users_fc1,
    tgt.pageviews_budget,
    tgt.pageviews_fc1,
    safe_divide(t.users_max_daily - tgt.users_budget,     tgt.users_budget)     as users_variance_vs_budget,
    safe_divide(t.users_max_daily - tgt.users_fc1,        tgt.users_fc1)        as users_variance_vs_fc1,
    safe_divide(t.pageviews_monthly - tgt.pageviews_budget, tgt.pageviews_budget) as pageviews_variance_vs_budget,
    safe_divide(t.pageviews_monthly - tgt.pageviews_fc1,    tgt.pageviews_fc1)    as pageviews_variance_vs_fc1
from traffic t
left join targets tgt
  on tgt.brand_key = t.brand_key
 and tgt.period    = t.period
