# Architecture

Three files land in a bucket. dbt turns them into one wide table. A Python script renders that table as HTML. That's the whole thing.

```
Financial CSV ──┐
Budget CSV    ──┼──> GCS raw/ ──> BigQuery raw.* ──> dbt ──> BigQuery marts.* ──> render.py ──> GCS public/
Traffic CSV   ──┘
```

## The layers, in dbt terms

**Raw.** Exactly what the source produced. Financial CSVs come from SAP with weird column names and mixed casing. We don't fix that here — we keep it messy so we can trace anything downstream back to the byte that produced it.

**Staging.** Cleaned. Column names in snake_case, types cast, one model per source. Any brand renaming, currency detection, or column-level filtering happens here. Nothing joins yet.

**Intermediate.** Where the joins live and where the business logic starts showing up. Financial actuals join to budgets on `(brand_key, period, pl_line)`. Traffic aggregates from daily to monthly. FX rates apply. Brand-specific revenue exclusions get filtered.

**Marts.** One row per brand per month, ready to render. `marts.monthly_kpi` is the star of the show — everything the report needs, one row per brand per month, no lookups required at read time.

Why three layers instead of one big query: staging is where you catch schema changes early, intermediate is where the business logic is visible and testable, marts is what everything downstream reads. If a KPI is wrong, you know which layer to look at. If you crammed everything into one 400-line query, you wouldn't.

## The warehouse choice

BigQuery. Serverless, on-demand pricing, GA4 has a native export into it, and at this scale the whole stack costs about CHF 300/month total. The equivalent Snowflake setup would cost more and add nothing we'd use. See [`decisions/0004-why-bigquery.md`](decisions/0004-why-bigquery.md) *(coming Area 2)*.

## The transformation choice

dbt. Every SQL model is version-controlled, testable, documented, and shows up in a lineage graph. The alternative is Python transforms — which is what production started as and got progressively unmanageable. See [`decisions/0005-why-dbt.md`](decisions/0005-why-dbt.md) *(coming Area 2)*.

## Data contract

Every raw source has a schema file. Ingestion fails loudly if the source drops a file that doesn't match. The dbt `sources.yml` re-declares expected columns and tests them (`not_null`, `accepted_values` on brand keys, `relationships` to dimension tables). If SAP suddenly renames `Sales Rev` to `Revenue Sales`, the pipeline stops instead of silently returning zero for revenue.

## What we don't do here

No streaming. No real-time updates. No incremental dbt models — full-refresh every month is cheap enough. No dimensional modeling (Kimball star schema) — the monthly grain is so wide and small (6 brands × 12 months × handful of metrics) that flat tables are easier to reason about. If we had 500 brands and 10-second latency requirements, everything about this would be different. We don't, so it isn't.
