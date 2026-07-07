# Sports Media KPI Monitor

Monthly traffic-light KPI report for a fictional 6-brand sports media group. Built as an end-to-end analytics-engineering portfolio: **synthetic data → BigQuery → dbt → static HTML report** on GCP.

## What it does

Each month, business stakeholders (CEO, brand MDs) open one page and see, per brand:

- 🟢🟡🔴 Revenue vs Budget (actual, variance %, forecast)
- 🟢🟡🔴 EBIT vs Budget
- 🟢🟡🔴 Traffic (unique users, YoY)
- Revenue diversification (betting vs advertising vs other)
- Currency-normalized (all brands → CHF)

Everything comes from three source shapes: a financial export (SAP-style), a budget spreadsheet, and web analytics (GA4-style).

## Stack

| Layer | Tool | Why |
|---|---|---|
| Ingestion | Python + GCS drops | See [`docs/decisions/0001-why-not-fivetran.md`](docs/decisions/0001-why-not-fivetran.md) |
| Warehouse | BigQuery | Serverless, cheap at this scale, native GA4 export |
| Transformation | dbt | SQL-first, testable, documented, industry standard |
| Orchestration | Cloud Scheduler + Cloud Functions | See [`docs/decisions/0002-why-not-airflow.md`](docs/decisions/0002-why-not-airflow.md) |
| Serving | Static HTML on GCS | See [`docs/decisions/0003-why-static-html-not-bi-tool.md`](docs/decisions/0003-why-static-html-not-bi-tool.md) |

## Live demo & repo

- **Report**: `https://sports-media-kpi-monitor.pages.dev/` (or wherever it ends up hosted)
- **Docs**: [`docs/`](docs/) — architecture, decisions, trade-offs
- **Portfolio context**: [`docs/portfolio.md`](docs/portfolio.md)

## Origin

Built as the public, anonymized version of a production KPI report I own for a European sports media group with 6 brands across 6 countries. All numbers here are synthetic.
