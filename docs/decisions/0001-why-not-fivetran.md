# ADR 0001 — Why we don't use Fivetran (or Airbyte, Rivery, Stitch)

**Status:** Accepted
**Date:** 2026-07-07

## Context

Managed EL (extract-load) tools like Fivetran, Airbyte, and Rivery are the industry default for ingesting SaaS and database sources into a warehouse. They provide:

- Pre-built connectors for hundreds of sources
- Automatic schema evolution
- Managed auth (OAuth refresh, key rotation)
- Idempotent incremental syncs
- Zero code to maintain

For a mid-sized data team, choosing "off-the-shelf ingestion" over "hand-rolled Python" is typically the right call — the engineering time saved pays for the license many times over.

## Decision

**We do not use Fivetran or a comparable managed EL tool.** Ingestion is bespoke Python running on Cloud Functions, plus native GCS file drops for CSV sources.

## Rationale

### 1. Cost profile doesn't justify the license

- Fivetran pricing scales with monthly active rows (MAR). For a 6-brand sports media company at our data volume, quoted pricing lands at **~$1,500-2,500/month**.
- Total GCP cost for the entire stack (including all pipelines) is **~CHF 300/month**.
- Adding Fivetran would 5-10× the total data-infra cost to save maintenance time on ~10 sources. Bad ROI.

### 2. Connector coverage is incomplete for our sources

- Our largest source (**GA4**) is best ingested via **Google's native GA4→BigQuery export** — free, real-time-ish, no third-party in the loop. Fivetran doesn't improve on this.
- Piano Analytics, SATI, JWPlayer legacy accounts, GAM, and OnNet don't all have first-class Fivetran connectors. We'd still need custom Python for the tail.
- Custom is the *only* option for the sources that matter most, so managed-connector savings apply to a smaller-than-headline share of ingestion work.

### 3. Our sources change infrequently

- Managed connectors shine when source schemas evolve constantly (Salesforce custom fields, Stripe product changes). Our sources are stable: GA4 has a fixed schema, SAP financials are contract-defined, ad-server APIs are versioned.
- Maintenance cost of hand-rolled ingestion is real but bounded (~2-4 hours/month across the stack).

### 4. We stay closer to the metal

- Hand-rolled ingestion lets us apply source-specific business rules early (Abola pageview dedup at ingestion time, currency normalization on load). A managed connector loads raw, and we'd re-apply these downstream anyway.
- Full control over retry logic, error alerting, and data-quality checks per source. With Fivetran, we'd be tuning inside their UI instead of Python we own.

## When we would revisit

- If we cross a threshold where **>10 new SaaS sources** need to be added in a year (Fivetran connector library becomes valuable).
- If we hire an engineer whose time costs > $2000/month of Fivetran (unlikely at our scale).
- If a specific source becomes so painful to maintain (auth refresh loops, schema drift) that a managed connector for that one source is worth it — in which case, use **Airbyte Open Source** self-hosted on Cloud Run for a single source, not a full Fivetran license.

## Trade-offs we accept

- **We own maintenance forever.** When Google deprecates the GA4 Data API v1beta, we fix our extractor. When Piano rotates auth, we update our client. This is real work.
- **We look less "modern" on paper.** In interviews, "we use Fivetran" is easier to say than "we hand-rolled ingestion in Python." We deliberately trade signaling for economics.
- **Scaling new sources is slower.** Adding a new brand requires writing an extractor. Fivetran would be minutes-to-set-up. This is fine at our current growth rate (roughly one new brand every 12-18 months).

## Alternatives considered

- **Fivetran** — rejected on cost (see above)
- **Airbyte Open Source, self-hosted on Cloud Run** — realistic future option; deferred until at least one source is painful enough to justify the Cloud Run + Kubernetes-lite overhead
- **Airbyte Cloud (managed)** — cheaper than Fivetran but same connector-gap issue
- **Meltano** (open-source, Singer-tap based) — considered; smaller connector library than Airbyte

## For the interview

> "We looked at Fivetran and Airbyte and decided against them for two reasons: at our data volume (~CHF 300/mo total GCP cost), the license would 5× our infra bill for maybe 20% engineering-time savings, and half our sources don't have first-class connectors anyway. We do use Google's native GA4→BigQuery export for our biggest source — that's the modern answer for GA4 on GCP. If we grew to a point where managed ingestion made sense, we'd start with Airbyte OS on Cloud Run for a single source and expand from there."
