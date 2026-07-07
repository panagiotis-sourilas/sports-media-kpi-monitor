# ADR 0003 — Why static HTML instead of a BI tool

Date: 2026-07-07

## Context

Looker, Metabase, Superset, Preset, Sigma, Tableau, Power BI — the modern data stack expects a BI tool at the serving layer. They give you dashboards with filters, drill-down, self-serve exploration, and sharing.

## Decision

We render a static HTML page. Python + Jinja + a bit of eCharts. No BI tool.

## Why

**Executives don't self-serve.** The CEO opens the report at 07:00 and reads it in 90 seconds. She does not click filters. She does not drill down. She wants an opinion — "the group is on plan, EBIT is worrying, Brand E needs attention" — not a dataset. A BI tool optimized for exploration is the wrong tool for a report that's answering the question, not helping someone find one.

**The audience is fixed.** Six MDs and one CEO. Not a shared workspace of 200 analysts. Every BI tool's user-management story is overkill.

**A static page is faster.** Zero server-side rendering, zero database round-trips at view time. The mart runs once a month; the HTML is regenerated once a month; the page loads in 200ms on a phone in the airport lounge. No BI tool comes close.

**A static page is cheaper.** GitHub Pages is free. Looker starts around $50/user/month. Metabase is open-source but self-hosting a real instance means a Cloud Run + a database + auth wiring. For a 7-user report that renders monthly, it's a lot.

**A static page prints.** Real finance meetings still print things. The report has a `@media print` stylesheet built in from day one. Try that in Looker.

## When we'd reconsider

If we grew to a real analytics team that needed to explore the data. If MDs started asking "can I filter by country?" or "can I see this by week?" — those are BI-tool questions. But we haven't been asked, and asking would be a good sign we've reached the scale where BI pays off.

If we needed embedded analytics inside another product — Metabase or Cube have real value there.

## What this costs us

No self-serve. If an MD wants to see last quarter's traffic mix by country, someone has to build it. In a Metabase world they'd click.

No SQL exploration UI for analysts. We assume anyone who wants raw numbers can write SQL against BigQuery directly — which is true for our audience but not for everyone's.

## Alternatives

**Metabase** — realistic if we wanted self-serve. Free tier is enough for our headcount. Hosting overhead is the reason we don't.

**Looker Studio (was Google Data Studio)** — free, GCP-native, connects to BigQuery in one click. The demo-ready choice if we didn't care about design. We do — the traffic-light layout is worth the custom render.

**Cube + a custom React app** — most modern, most control. Also most work. If the report became a product, this is where we'd land.

**Notion embed** — considered as a joke, then seriously. Rejected because Notion can't do the traffic-light logic without an iframe of a page we'd still have to build.
