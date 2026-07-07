# Why this repo exists

There's a monthly KPI report at work I own. Six brands, six countries, financial data from SAP, budget from Excel, traffic from GA4. The CEO and the six MDs open it every month and decide what to worry about. It's the report I get pulled into meetings about.

I can't put the real one on GitHub — real financials, real brand names, real internal domains. So this is a rebuild with synthetic data and generic brand names. The design decisions, the trade-offs, and the code shape stay identical.

## What's in here

Architecture decisions written down. The stack could easily be Fivetran + Snowflake + dbt Cloud + Looker — that's the industry default. The ADRs in [`decisions/`](decisions/) explain why we're not doing that at this scale, with real numbers. Some of those calls would flip if we were bigger or had more budget.

Business logic modeled in SQL. Currency normalization (multiple local currencies, one report currency), budget-to-actual matching by brand and month and P&L line, revenue exclusions that vary per brand. Not just querying data — shaping it into something usable.

Docs written the way I'd write them if I was handing this off to another engineer. Short, opinionated, honest about what it costs us. If something reads like it came out of a template, that's a bug.

## What's not in here

Not streaming. The real report is monthly. Making the demo streaming would be pretending to solve a problem that doesn't exist.

Not multi-tenant. One company, one report. The production version has per-brand access rules; the demo doesn't need them.

Not a BI dashboard. No filters, no drill-down, no click-to-explore. It's a static page. Executives don't self-serve — they get sent a link and open it. ADR on this choice is a follow-up.
