# ADR 0003 — Why static HTML instead of a BI tool

Date: 2026-07-07

## Context

Looker, Metabase, Superset, Sigma, Tableau, Power BI. The modern data stack expects a BI tool at the serving layer — dashboards, filters, drill-downs, self-serve exploration.

## Decision

Static HTML rendered by Python + Jinja + eCharts. No BI tool.

## Why

The audience doesn't explore. The CEO and six MDs read the report in 90 seconds and decide what to worry about. They don't filter, they don't drill. Optimizing for exploration is solving a problem that doesn't exist here.

Fixed audience. Seven users, all named. The user-management, SSO, and permissioning story of any BI tool is overkill for that.

Speed. A static page renders in 200ms on a phone. Every BI tool round-trips through a query engine. Executives read in the morning on their commute — latency matters more than interactivity.

Cost. GitHub Pages is free. Looker starts around $50/user/month. Metabase is free but self-hosting a real instance means Cloud Run + a database + auth — not zero effort at any scale.

It prints. Real finance meetings still print things. A `@media print` stylesheet works out of the box. Try that in Looker.

## When we'd reconsider

MDs start asking "can I filter by country?" or "can I see this by week?" — those are BI questions and would be a good signal we've grown into the tool. Or if we needed embedded analytics inside another product, at which point Cube or Metabase Embedding earn their place.

## What this costs us

No self-serve. If someone wants last quarter's traffic mix by country, someone builds it. No SQL exploration UI for the curious.

## Alternatives

**Metabase** — realistic if we wanted self-serve without paying Looker prices. Hosting overhead is why we haven't.

**Looker Studio (ex-Data Studio)** — free, GCP-native. The demo-ready choice if we didn't care about design. We do.

**Notion embed** — considered as a joke, then briefly seriously. Rejected because Notion can't do the traffic-light logic without embedding a page we'd still have to build.
