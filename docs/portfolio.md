# Why this repo exists

I own a monthly KPI report at work. Six brands, six countries, financial data from SAP, budget from Excel, traffic from GA4. The CEO and the six MDs open it every month and decide what to worry about. It's the report I get pulled into meetings about.

I can't put it on GitHub — real financials, real brand names, real internal domains. So I rebuilt it here with synthetic data and generic brand names, keeping the design decisions and the trade-offs intact. If you're a hiring manager or a data engineer trying to figure out how I think, this is the thing to look at.

## What I hope you take away

**I make architecture decisions based on numbers, not defaults.** The stack could be Fivetran + Snowflake + dbt Cloud + Looker. Every ADR in `docs/decisions/` explains why we're not doing that, with real cost numbers. If we were a bigger team or had more budget, several of those calls would flip. That's the point — I want you to see the reasoning.

**I can model business logic in SQL, not just query it.** Currency normalization (EUR and RSD amounts, CHF report), budget-to-actual matching by brand/month/P&L line, revenue exclusions that vary by brand (Abola's user market revenue doesn't count toward RpM, for example — that lives in dbt). This is the stuff analytics engineering roles hire for.

**I write docs like a human, not a wiki.** Short, opinionated, honest about the costs. If a doc looks like it was generated in five seconds by a model, I've failed. Skim [`decisions/0001-why-not-fivetran.md`](decisions/0001-why-not-fivetran.md) — that's the voice.

## What this repo isn't

**Not streaming.** The real report is monthly. Making the demo streaming would be pretending to solve a problem that doesn't exist here.

**Not multi-tenant.** One company, one report. No user auth, no per-brand access rules in the demo. The production version has those — see [`docs/decisions/0002-why-not-airflow.md`](decisions/0002-why-not-airflow.md) *(coming Area 3)* for the access story.

**Not a BI dashboard.** No filters, no drill-down, no click-to-explore. It's a page you read. That's on purpose. Executives don't self-serve, they get sent a link. See [`decisions/0003-why-static-html-not-bi-tool.md`](decisions/0003-why-static-html-not-bi-tool.md) *(coming Area 5)*.

## How to talk to me about this

The best question you can ask is *"why did you pick X over Y."* Every choice here has a paragraph of reasoning behind it, and I'd rather explain that than defend a shiny stack diagram.

The second-best question is *"what would break first at 10× the data."* I have opinions.
