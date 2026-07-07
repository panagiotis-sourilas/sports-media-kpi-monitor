-- The 4 revenue lines should sum to total revenue. When they don't, a new
-- revenue line has been added upstream without being wired into the mart.
-- 0.5% tolerance for FX rounding.

with mart as (
    select * from {{ ref('marts_monthly_kpi') }}
),

check_rows as (
    select
        period,
        brand_key,
        revenue_chf,
        coalesce(advertising_revenue_chf, 0)
          + coalesce(betting_revenue_chf, 0)
          + coalesce(subscription_revenue_chf, 0)
          + coalesce(other_revenue_chf, 0) as parts_sum
    from mart
    where revenue_chf is not null and revenue_chf > 0
)

select *
from check_rows
where abs(parts_sum - revenue_chf) / revenue_chf > 0.005
