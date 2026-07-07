# Portfolio Context

## What this repo is

This is the **anonymized, open-source re-implementation** of a production monthly KPI report I built and own for a European sports media group. The production version is used by the CEO and 6 brand managing directors to run the business.

The public version:

- Uses **fully synthetic data** (see `ingestion/synthetic_data/`).
- Renames the 6 real brands to `Brand A/B/C/D/E/F` with fictional country flags.
- Multiplies real revenue figures by a random (but reproducible-with-seed) factor.
- Strips all real employee names, org references, and internal domains.

## What it demonstrates

| Skill | Where to look |
|---|---|
| **Analytics engineering with dbt** | [`dbt/`](../dbt/) — staging + intermediate + marts layout |
| **Warehouse thinking (BigQuery)** | [`docs/architecture.md`](architecture.md), partitioning + clustering choices |
| **Business-rule modeling** | [`dbt/models/marts/`](../dbt/models/) — currency FX, budget-to-actual matching, brand-specific exclusions |
| **Documenting decisions** | [`docs/decisions/`](decisions/) — ADRs explaining why we picked / rejected each tool |
| **Report generation** | [`serving/`](../serving/) — Jinja + Plotly → static HTML on GCS |
| **Testing & data contracts** | [`dbt/tests/`](../dbt/) + schema definitions |
| **Cost-aware architecture** | Decisions grounded in real economics, not defaults |

## What it does NOT demonstrate

Honest about the trade-offs:

- **No streaming** — everything is batch (monthly). The production version is monthly by design. Streaming would be pretending.
- **No custom BI dashboards** — we render static HTML deliberately (see [`decisions/0003-why-static-html-not-bi-tool.md`](decisions/0003-why-static-html-not-bi-tool.md)). If the target role requires Looker/Tableau, this repo won't show it.
- **No orchestrator** in the modern-stack sense (no Airflow / Dagster / Prefect). We use Cloud Scheduler + Cloud Functions. See [`decisions/0002-why-not-airflow.md`](decisions/0002-why-not-airflow.md).
- **No ingestion tool** in the modern-stack sense (no Fivetran / Airbyte). Same rationale — see [`decisions/0001-why-not-fivetran.md`](decisions/0001-why-not-fivetran.md).

## How to talk about this in interviews

**One-sentence pitch:**
> "I built and open-sourced an anonymized version of the monthly KPI report I own for a 6-brand European sports media group — it demonstrates end-to-end analytics engineering: synthetic data generation, BigQuery + dbt modeling with business rules for currency and budget-to-actual matching, and a rendered HTML report on GCS. The design decisions are all in ADRs, so you can see why I picked what I picked."

**When asked "why didn't you use [X]":**
> Point at the ADR. That's why they exist.

**When asked "what's the biggest limitation":**
> "It's monthly batch. If the business needed real-time, the shape of the whole thing would change — streaming ingestion, incremental dbt models, a warehouse designed for concurrent reads. I chose not to fake that."
