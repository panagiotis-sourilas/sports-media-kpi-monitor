-- Daily traffic rolled up to monthly per brand.
-- Users is COUNT(DISTINCT ...) in real GA4 — here we take a max-daily as a
-- reasonable proxy since the synthetic data has no cross-day dedup.
-- Sessions and pageviews are additive.

with daily as (
    select * from {{ ref('stg_traffic') }}
),

by_month as (
    select
        date_trunc(event_date, month) as period,
        brand_key,
        country,
        -- ponytail: max daily users ≈ MAU proxy for synthetic data.
        -- upgrade to HLL_COUNT.MERGE_UNION() sketches when we join real GA4.
        max(users) as users_max_daily,
        sum(sessions) as sessions_monthly,
        sum(pageviews) as pageviews_monthly
    from daily
    group by 1, 2, 3
)

select * from by_month
