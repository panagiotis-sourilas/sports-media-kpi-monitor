# ADR 0001 — Why we don't use Fivetran

Date: 2026-07-07

## Context

The default 2020s answer for pulling SaaS data into a warehouse is Fivetran (or Airbyte, or Rivery). Managed connectors, auto schema updates, no code. Every "modern data stack" diagram on the internet starts here.

## Decision

We don't use it. Ingestion is Python in Cloud Functions plus native GCS drops.

## Why

Two reasons that both need to be true.

**The math doesn't work at this size.** Fivetran quoted us around $1,500/month for our row volume. Total GCP bill including everything else is about CHF 300/month. Paying 5× the total infra cost to save maybe 10 hours/month of engineering time isn't a decision, it's a mistake.

**Half our sources aren't in the connector catalog anyway.** GA4 has a first-party BigQuery export from Google — Fivetran would be strictly worse than the free native option. Piano Analytics, SATI, JWPlayer legacy accounts, GAM, OnNet — all custom. We'd still write Python for those, and Fivetran only handles the shrinking rest.

The combination is what kills it. Either problem alone might be surmountable. Both together mean we're paying a lot to solve a small part of the problem badly.

## When we'd reconsider

If we start onboarding 5+ new SaaS sources a year. Or if a specific source gets so painful (auth loops, schema drift) that a single-source Airbyte deployment on Cloud Run pays for itself.

## What this costs us

Maintenance forever. When Google deprecates a GA4 API version, we fix it. When Piano rotates auth, we fix it. Adding a new brand takes a day of extractor writing instead of 10 minutes of clicking. That's real, and I'm not going to pretend it's not.

## Alternatives

Airbyte OSS on Cloud Run is the realistic middle path if we ever need managed ingestion for one specific source without paying for a full license. Airbyte Cloud is cheaper than Fivetran but has the same connector gap for our sources. Meltano has a smaller catalog and the same problem.
