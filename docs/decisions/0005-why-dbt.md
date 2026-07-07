# ADR 0005 — Why dbt

Date: 2026-07-07

## Context

The transform layer sits between raw tables and the report. The classic options: Python scripts (pandas / SQL string interpolation), stored procedures inside the warehouse, or dbt.

## Decision

dbt. Every transform is a `.sql` file version-controlled in the repo. dbt turns those files into a dependency graph, runs them in the right order, and tests the output.

## Why

**SQL is the honest layer.** Financial rules ("betting revenue counts, user market revenue doesn't"), currency normalization, budget-to-actual matching — these are all set-operations on tables. In Python they become dataframe joins with `merge()` calls, three levels of function nesting, and hidden business logic. In SQL they read like the specification: "join actuals to budget on brand + period + P&L line, sum where category = revenue." Anyone who can read SQL can read the transforms. That's not true of Python.

**Tests come for free.** dbt has `not_null`, `unique`, `accepted_values`, and `relationships` tests built in. Declare them in a YAML file and they run on every model. If SAP renames a column, the pipeline fails at the staging test, not silently downstream. In a Python pipeline you'd have to write these tests by hand.

**Lineage graph is real.** `dbt docs serve` opens a visual graph of every model, its columns, and what depends on it. If someone asks "what tables does the monthly KPI mart come from," the answer is a URL, not a Slack thread. Python pipelines have no equivalent unless you build one.

**Version control on business logic.** Every FX rate change, every revenue-line exclusion, every renamed column shows up in git blame with the commit message. Nobody's editing an Excel-based transform in place anymore.

**It's the industry default for analytics engineering.** dbt is on every data engineering job description. Learning it means every interview conversation is easier.

## When we'd reconsider

If the transforms became so complex that SQL stopped being readable. Some things are genuinely painful in SQL — recursive graph traversal, ML feature engineering, complex string parsing. Those move to Python (via `dbt-fal` or upstream in a Cloud Function) and dbt stays for the rest.

If we moved to a warehouse that didn't have a dbt adapter. dbt-core supports BigQuery, Snowflake, Redshift, Postgres, Databricks, Spark. Everything realistic is covered.

## What this costs us

Another tool to install, another config file to maintain. `profiles.yml` has credentials, so it can't live in the repo — that's mild friction on onboarding. Materializations matter: get the `+materialized: view` vs `table` wrong and you either burn query cost or serve stale data. This is real but learnable.

The bigger cost is discipline: dbt encourages "one model, one file, one purpose." It's tempting to write a giant model that does five things. That's how Python transforms got unmaintainable in the first place; nothing about dbt stops it, only the person writing the model does.

## Alternatives

Python with pandas would work at small scale. Business logic hides in function bodies instead of SQL text. No lineage graph, no free tests, no adapter portability. Fine for prototyping, painful at any scale.

Stored procedures inside the warehouse would keep transforms close to the data but lose version control (they live in the warehouse, not in git) and lose the lineage graph.

SQLMesh is a newer competitor. Similar model, adds runtime-safety features (blue-green deploys, automatic column-level lineage). Realistic option if starting fresh in 2026 — I'd consider it for a greenfield project. dbt has the ecosystem lead for now.
