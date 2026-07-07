# Seeds

Reference tables loaded into BigQuery via `dbt seed`. Version-controlled data
that doesn't come from a source system.

## `fx_rates.csv`

Monthly local-to-CHF conversion rates. 24 months × 4 currencies. Approximate historicals.

## `traffic_targets.csv`

Monthly Users and Pageviews targets per brand. 24 months × 6 brands × 2 metrics × 2 comparison columns (Budget + FC1).

### How the targets are set

Same shape as financial planning:

- **Budget** — set once at the start of the year during annual planning. Doesn't change through the year.
- **FC1** — mid-year re-forecast. Slightly more informed than Budget, usually 1–2% higher on traffic assumptions.

### The sporting calendar shape

Sports media traffic is deeply seasonal. The target curve reflects it:

- **August peak** — European league starts + summer transfer window closing
- **June bump** — Euros, Copa América, or World Cup (year-dependent)
- **January dip** — post-season low, before the winter transfer window
- **December mild lift** — holiday reading + end-of-year retrospectives

Peak-to-trough ratio is roughly 1.3× on both users and pageviews. Brand-size scaling
matches the financial seed (Brand A = full scale, Brand E = ~35% of A).

### Refreshing

New year's targets get added to this file during the annual planning cycle.
Mid-year FC1 updates rewrite the FC1 column only, leaving Budget frozen.
