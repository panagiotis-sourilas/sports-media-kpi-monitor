# ADRs

Each file here captures one decision. Why we picked this thing, what we didn't pick and why, when we'd change our minds. Written when the decision was made — we don't edit them later. If we reverse a call, we write a new ADR that supersedes the old one.

## Index

| # | Decision | Status |
|---|---|---|
| [0001](0001-why-not-fivetran.md) | Why we don't use Fivetran | Accepted |
| 0002 | Why we don't use Airflow | *Area 3* |
| 0003 | Why static HTML instead of a BI tool | *Area 5* |
| 0004 | Why BigQuery | *Area 2* |
| 0005 | Why dbt | *Area 2* |

## Why ADRs exist at all

Because six months later, someone (usually me) asks *"why on earth did we pick X"* and there's no answer. ADRs are the answer. Written when the reasoning is fresh, kept short enough that people actually read them.

Real production ADRs at work stop after the alternatives. The last section in these public ones — "In an interview" — is portfolio-specific.

## What ADRs are for

Decisions that would take an hour to re-justify from scratch. Not every commit. Not every refactor. If you're going to have to defend the choice in a meeting six months out, write one.
