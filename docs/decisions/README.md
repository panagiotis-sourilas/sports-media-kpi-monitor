# Architecture Decision Records (ADRs)

Each ADR captures **one decision, one reason, one moment in time**. If we change our mind, we don't edit the ADR — we write a new one that supersedes it.

## Index

| # | Decision | Status |
|---|---|---|
| [0001](0001-why-not-fivetran.md) | Why we don't use Fivetran (or other managed EL) | Accepted |
| 0002 | Why we don't use Airflow (or Dagster / Prefect) | *pending — Area 3* |
| 0003 | Why we render static HTML instead of using a BI tool | *pending — Area 5* |
| 0004 | Why BigQuery (not Snowflake / Redshift / Databricks) | *pending — Area 2* |
| 0005 | Why dbt (not raw Python transforms) | *pending — Area 2* |

## Format

Each ADR follows:

1. **Context** — what problem exists
2. **Decision** — what we chose
3. **Rationale** — why (with real numbers, not vibes)
4. **When we would revisit** — the trigger conditions to overturn this
5. **Trade-offs we accept** — the honest costs
6. **Alternatives considered** — one line each on the options we rejected
7. **For the interview** — a scripted way to explain it

The last section is portfolio-specific. Real production ADRs stop at step 6.
