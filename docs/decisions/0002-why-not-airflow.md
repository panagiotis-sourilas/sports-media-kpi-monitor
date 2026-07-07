# ADR 0002 — Why we don't use Airflow

Date: 2026-07-07

## Context

Airflow is the default orchestrator. Dagster and Prefect are the modern challengers. You run one when your pipeline has enough moving parts that you need a UI to see what ran, what failed, and where to restart.

## Decision

We don't. The pipeline is a straight-line script chain: `dbt seed && dbt run && dbt test && python serving/render.py`. In production this becomes a GitHub Actions cron job.

## Why

The DAG is a straight line. Five steps, no branches, no fan-out. A DAG UI shows the same thing as `cat` on a shell script.

The schedule is monthly. Airflow's operational value scales with schedule complexity — hourly ingestion, retries with backoff, SLA alerts, timezone-aware dependencies. None of that applies.

Cost. Cloud Composer starts at ~$300/month for the smallest environment — that's our entire GCP bill. Self-hosted Airflow means running a scheduler, a metadata DB, and workers. Not free even at "free."

GitHub Actions covers what we need. Cron trigger, run the chain, commit the output, fail loudly on error. Free for public repos.

## When we'd reconsider

More than 10 distinct pipeline schedules, fan-out to parallel ingestion, or the first real "we need to see what ran when" incident. Any one of those tips the ROI.

If we ever needed lineage-aware retries, I'd skip Airflow and go to Dagster.

## What this costs us

No pretty DAG picture. No smart retry policy. If the render fails, next month's run tries again.

## Alternatives

**Cloud Scheduler + Cloud Functions** — GCP-native equivalent. GitHub Actions wins on "code and trigger in the same repo."

**Dagster** — better assets-not-tasks model, first-class dbt integration, better retries. This is where we'd land if we outgrew scripts.

**Prefect** — similar shape, weaker adoption. No reason to pick it over Dagster.
