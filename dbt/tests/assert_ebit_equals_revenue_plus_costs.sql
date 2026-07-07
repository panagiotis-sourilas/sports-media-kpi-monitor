-- EBIT = revenue + costs (costs are stored as negative).
-- Fails when a new P&L category slips into raw without being categorized,
-- or when the SAP sign convention flips.

with mart as (
    select * from {{ ref('marts_monthly_kpi') }}
)

select *
from mart
where revenue_chf is not null
  and costs_chf is not null
  and abs((revenue_chf + costs_chf) - ebit_chf) > 1  -- 1 CHF rounding tolerance
