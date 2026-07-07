# ADR 0004 — Why BigQuery

Date: 2026-07-07

## Context

Every warehouse-based data project needs a warehouse. The current options: BigQuery on GCP, Snowflake (cloud-agnostic), Redshift on AWS, Databricks SQL, or Postgres if you're brave and small.

## Decision

BigQuery.

## Why

**GA4 has a native BigQuery export.** In sports media, GA4 is the biggest data source by row count. Google publishes a first-party connector that streams events into BigQuery daily, for free. Snowflake and Redshift don't have this — you'd have to build the GA4 pipeline yourself (custom, or via Fivetran, which we've already ruled out). Picking any warehouse that isn't BigQuery means either running two pipelines for GA4 or paying for a connector we don't need.

**On-demand pricing works at our scale.** BigQuery charges per TB scanned, no idle cost. Total data volume is small (thousands of financial rows, tens of thousands of traffic rows per month) — the 1 TB/month free tier covers everything with room to spare. Snowflake charges for compute time (virtual warehouses), which we'd be paying for even when nobody queries. At our scale, on-demand beats reserved every time.

**Serverless matters when you're solo.** No clusters to size, no scale-up/scale-down, no compute credits to buy. Push data, run queries, done. Databricks and Snowflake both require thinking about compute. BigQuery doesn't.

## When we'd reconsider

If we grew 10× and started paying real query bills. On-demand becomes expensive past a certain query volume — some companies hit that ceiling and switch to BigQuery flat-rate slots, or move to Snowflake for cheaper compute. Neither applies at CHF 300/month total infra.

If we needed real-time analytics on incoming events. BigQuery streaming inserts have a cost per row that would add up at 1M+ events/hour. We do batch, so this doesn't hit us.

## What this costs us

Portability. BigQuery SQL is 95% standard but has quirks (`STRUCT`, array functions, `_TABLE_SUFFIX` for sharded tables). If we ever migrate to Snowflake we'd rewrite parts of the SQL. Locking to GCP is a real trade-off — but at this scale, the cost of migrating is a hypothetical and the cost of using GCP is a monthly bill under CHF 300.

## Alternatives

Snowflake would give us cloud-agnostic SQL and cheaper compute at high volumes, but no GA4 native export and non-trivial idle cost. Redshift is fine but tied to AWS and we're already in GCP. Databricks is a lakehouse, not a warehouse — different tool for different problems. Postgres is not a warehouse; it works until it doesn't.
