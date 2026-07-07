# dbt project

Three-layer SQL project. Reads from `raw_*` in BigQuery, writes cleaned models to `staging_*`, joined models to `intermediate_*`, and business-facing tables to `marts_*`.

## Layout

```
models/
  staging/       one model per source, cleaned
  intermediate/  joins + business logic
  marts/         one row per brand per month
```

Every model is a `.sql` file. `_sources.yml` declares what BigQuery tables to read from. `_models.yml` files describe each model's columns and tests.

## First run — one-time setup

You need Python 3.12 (dbt doesn't support 3.14 yet). If you have another Python around, use it. Otherwise install 3.12 in a venv.

```bash
# Create a venv with Python 3.12 in it
py -3.12 -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # macOS/Linux

pip install dbt-bigquery
```

Then copy the sample profile and fill in your service-account key path:

```bash
mkdir -p ~/.dbt
cp dbt/profiles.yml.example ~/.dbt/profiles.yml
# edit ~/.dbt/profiles.yml — set `keyfile` to your service-account JSON path
```

## Running

```bash
cd dbt

dbt debug        # sanity check the connection
dbt run          # build all models
dbt test         # run all data tests
dbt docs generate && dbt docs serve   # open the lineage graph in your browser
```

## What each layer does

- **staging** (`stg_*`) — one model per source. Renames columns to snake_case, casts types, filters obvious garbage. No joins.
- **intermediate** (`int_*`) — joins + business rules. Currency conversion, budget-to-actual matching, revenue-mix flags.
- **marts** (`marts_*`) — one row per brand per month, ready to be rendered.

The layer split is a dbt convention. If a KPI is wrong you know which layer to look at.
