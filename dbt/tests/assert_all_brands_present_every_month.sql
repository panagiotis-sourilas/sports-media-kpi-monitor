-- Every month must have all 6 brands. Catches silent-zero regressions
-- where a brand disappears from the report and nobody notices.

with per_month as (
    select
        period,
        count(distinct brand_key) as brand_count
    from {{ ref('marts_monthly_kpi') }}
    group by period
)

select *
from per_month
where brand_count != 6
