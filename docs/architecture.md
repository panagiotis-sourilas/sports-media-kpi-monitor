# Architecture

## The picture

```
┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
│ Financial CSV       │   │ Budget CSV          │   │ Traffic CSV (GA4)   │
│ (monthly SAP drop)  │   │ (annual, in CSV)    │   │ (daily, GA4-style)  │
└──────────┬──────────┘   └──────────┬──────────┘   └──────────┬──────────┘
           │                         │                         │
           └───────── GCS bucket / raw/ ─────────────┬────────┘
                                                    │
                                                    ▼
                                       ┌────────────────────────┐
                                       │ BigQuery (raw dataset) │
                                       │  raw.financial         │
                                       │  raw.budget            │
                                       │  raw.traffic           │
                                       └────────────┬───────────┘
                                                    │
                                                    ▼
                                       ┌────────────────────────┐
                                       │ dbt (transform)        │
                                       │  staging/ → cleaning   │
                                       │  intermediate/ → joins │
                                       │  marts/ → business     │
                                       └────────────┬───────────┘
                                                    │
                                                    ▼
                                       ┌────────────────────────┐
                                       │ BigQuery (marts)       │
                                       │  marts.monthly_kpi     │
                                       │  marts.revenue_mix     │
                                       └────────────┬───────────┘
                                                    │
                                                    ▼
                                       ┌────────────────────────┐
                                       │ Python render script   │
                                       │  → static HTML report  │
                                       └────────────┬───────────┘
                                                    │
                                                    ▼
                                       ┌────────────────────────┐
                                       │ GCS (public bucket)    │
                                       │  → viewed by CEO/MDs   │
                                       └────────────────────────┘
```

## Layers

- **Raw**: exactly what the source produced. No cleaning. If it was messy, we keep it messy here.
- **Staging (dbt)**: rename columns to snake_case, cast types, filter obvious garbage.
- **Intermediate (dbt)**: join across sources, apply business rules (currency normalization, brand-specific exclusions, budget-to-actual matching).
- **Marts (dbt)**: business-shaped tables. One row per brand per month. Ready for BI or a report generator.
- **Serving**: render the marts into a human-readable page.

## Data contract

Every raw source has a **schema in `ingestion/synthetic_data/schemas/`**. If the source drops a file that doesn't match, ingestion fails loudly — no silent corruption of downstream marts.

## Why this shape

- **Separation of "raw / staging / marts"** is the dbt convention. It's the industry default for a reason: it makes lineage traceable ("this KPI came from that row of that source"), and it lets you fix a business rule without touching ingestion.
- **BigQuery as warehouse** is chosen for cost + serverless simplicity at this scale. See [`decisions/0004-why-bigquery.md`](decisions/0004-why-bigquery.md).
- **dbt in the middle** is the load-bearing modernization vs a monolithic Python-transforms setup. See [`decisions/0005-why-dbt.md`](decisions/0005-why-dbt.md).
