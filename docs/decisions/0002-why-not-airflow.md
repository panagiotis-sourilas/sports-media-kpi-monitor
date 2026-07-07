# ADR 0002 — Why we don't use Airflow

Date: 2026-07-07

## Context

Airflow is the default orchestrator for data pipelines. Dagster and Prefect are the modern challengers. The reason to run one: your pipeline has enough moving parts that you need a UI to see what ran, what failed, and where to restart.

## Decision

We don't run an orchestrator. The pipeline is a small script chain: `dbt seed && dbt run && dbt test && python serving/render.py`. On production this becomes a GitHub Actions cron job that runs the same chain monthly.

## Why

**Airflow makes sense when your DAG has branches or dependencies you need to visualize.** Ours is a straight line: seeds → staging → intermediate → marts → render. Five steps, no branches, no fan-out. A DAG UI adds nothing.

**The report runs monthly.** Airflow's operational value scales with schedule complexity — hourly ingestion of 40 sources across time zones, retries with backoff, SLA alerts. None of that applies to a monthly page render.

**Managed Airflow costs money we don't have.** Cloud Composer starts at ~$300/month for the smallest environment. That's the entire GCP infra bill we're targeting. Self-hosted Airflow costs a Cloud Run instance plus the maintenance burden of running a distributed scheduler.

**GitHub Actions covers 100% of what we need.** Cron trigger, run script, commit output, fail loudly on error. Free for public repos. Zero infra.

## When we'd reconsider

If we grew past ~10 distinct pipeline schedules, or added fan-out (parallel ingestion from multiple sources), or hit a real "we need to see what ran when" incident. Any one of those tips the ROI toward a real orchestrator.

If we needed lineage-aware retries — Dagster's model beats Airflow here — that's when we'd skip Airflow entirely and go straight to Dagster.

## What this costs us

No pretty DAG picture in the docs. No retry-with-backoff for free. If the render fails, the next scheduled run just tries again — no smart replay logic.

## Alternatives

**Cloud Scheduler + Cloud Functions** — GCP-native, similar cost. Good if we were staying in GCP for everything. GitHub Actions edges it out because the code and the trigger live in the same repo.

**Dagster** — better mental model (assets, not tasks), better retries, uses SQL-first primitives that match dbt. Realistic future if we grow enough to need an orchestrator.

**Prefect** — similar to Dagster, weaker adoption, no compelling reason to pick it over Dagster.

**Windmill / Kestra** — newer, worth watching, not yet worth adopting.
