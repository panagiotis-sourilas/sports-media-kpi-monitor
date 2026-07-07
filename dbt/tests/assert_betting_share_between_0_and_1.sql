-- Betting share is a ratio in [0, 1]. Outside that range means the
-- numerator and denominator use different currency scales.

select *
from {{ ref('marts_monthly_kpi') }}
where betting_share is not null
  and (betting_share < 0 or betting_share > 1)
