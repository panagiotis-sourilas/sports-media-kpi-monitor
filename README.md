# Sports Media KPI Monitor

Every month the CEO and six brand MDs at a European sports media group open one page and see whether the business is on plan. This is the public, anonymized rebuild of that page.

Real names removed, revenue numbers scrambled with a fixed seed, brands renamed A through F. Everything else works the same as production.

## What it does

- Reads a monthly financial export (SAP-style), a frozen annual budget, and daily traffic (GA4-style).
- Cleans and models in dbt on BigQuery.
- Renders a static HTML page: revenue vs budget, EBIT vs budget, traffic vs last year, revenue mix, all normalized to CHF.
- Uploads to GCS. Anyone with the link opens it in the browser.

No BI tool. No dashboard subscription. It's a page.

## Stack

| Layer | Choice | Why not the obvious alternative |
|---|---|---|
| Ingestion | Python + GCS file drops | [Not Fivetran](docs/decisions/0001-why-not-fivetran.md) |
| Warehouse | BigQuery | [Not Snowflake](docs/decisions/0004-why-bigquery.md) *(coming Area 2)* |
| Transform | dbt | [Not Python transforms](docs/decisions/0005-why-dbt.md) *(coming Area 2)* |
| Orchestrate | Cloud Scheduler + Cloud Functions | [Not Airflow](docs/decisions/0002-why-not-airflow.md) *(coming Area 3)* |
| Serve | Static HTML on GCS | [Not Looker / Metabase](docs/decisions/0003-why-static-html-not-bi-tool.md) *(coming Area 5)* |

The pattern: every layer picks the cheapest thing that works. Then explains why we didn't buy the modern default. Those explanations are the point — [see the ADRs](docs/decisions/).

## Where to look

- [`docs/architecture.md`](docs/architecture.md) — the whole pipeline in one diagram
- [`docs/decisions/`](docs/decisions/) — why each tool, why not the alternatives
- [`docs/portfolio.md`](docs/portfolio.md) — what this is meant to show, and what it isn't
- [`dbt/`](dbt/) *(coming Area 2)* — the actual models
- [`serving/`](serving/) *(coming Area 5)* — the render script

## The real version

Built for a real company. The production one runs monthly, feeds the exec team, uses live financials from SAP FC1 and GA4 across six brands in six countries. This repo is the same pipeline rebuilt without the confidential parts, so the design is visible without the numbers.
