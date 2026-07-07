# ADRs

Each file here captures one decision. Why we picked this thing, what we didn't pick and why, when we'd change our minds. Written when the decision was made — we don't edit them later. If we reverse a call, we write a new ADR that supersedes the old one.

## Index

| # | Decision | Status |
|---|---|---|
| [0001](0001-why-not-fivetran.md) | Why we don't use Fivetran | Accepted |
| [0002](0002-why-not-airflow.md) | Why we don't use Airflow | Accepted |
| [0003](0003-why-static-html-not-bi-tool.md) | Why static HTML instead of a BI tool | Accepted |
| [0004](0004-why-bigquery.md) | Why BigQuery | Accepted |
| [0005](0005-why-dbt.md) | Why dbt | Accepted |

## Why ADRs exist at all

Because six months later, someone (usually me) asks *"why on earth did we pick X"* and there's no answer. ADRs are the answer. Written when the reasoning is fresh, kept short enough that people actually read them.

## What ADRs are for

Decisions that would take an hour to re-justify from scratch. Not every commit. Not every refactor. If you're going to have to defend the choice in a meeting six months out, write one.
