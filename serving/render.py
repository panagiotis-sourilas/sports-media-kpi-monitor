"""Render the monthly KPI report from marts_monthly_kpi.

Queries BigQuery, applies traffic-light thresholds, renders a Jinja
template to a single self-contained HTML file.

Usage:
    python serving/render.py                       # renders latest month
    python serving/render.py --period 2026-05-01   # renders a specific month
    python serving/render.py --upload              # also uploads to GCS
"""
from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path

from google.cloud import bigquery, storage
from jinja2 import Environment, FileSystemLoader, select_autoescape


PROJECT = os.environ.get("GCP_PROJECT_ID", "inc-182120-panagiotis-sourilas")
MARTS_DATASET = "sports_media_kpi_monitor"
BUCKET = os.environ.get("REPORT_BUCKET", "sports-media-kpi-monitor-reports")
HERE = Path(__file__).parent

# Traffic-light thresholds — variance % (actual vs budget).
# Values worse than -5% start yellow, worse than -15% go red.
def status(variance_pct: float | None) -> str:
    if variance_pct is None:
        return "gray"
    if variance_pct >= -0.05:
        return "green"
    if variance_pct >= -0.15:
        return "yellow"
    return "red"


def latest_period(client: bigquery.Client) -> date:
    """Find the most recent period in the mart."""
    sql = f"""
    SELECT MAX(period) AS latest
    FROM `{PROJECT}.{MARTS_DATASET}.marts_monthly_kpi`
    """
    row = list(client.query(sql).result())[0]
    return row.latest


def fetch_month(client: bigquery.Client, period: date) -> list[dict]:
    """Pull one row per brand for the given month."""
    sql = f"""
    SELECT
      brand_key,
      country,
      revenue_chf,
      budget_revenue_chf,
      revenue_variance_pct,
      ebit_chf,
      budget_ebit_chf,
      ebit_variance_pct,
      betting_share,
      users,
      sessions,
      pageviews
    FROM `{PROJECT}.{MARTS_DATASET}.marts_monthly_kpi`
    WHERE period = @period
    ORDER BY brand_key
    """
    job = client.query(sql, job_config=bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("period", "DATE", period)]
    ))
    rows = []
    for r in job.result():
        d = dict(r)
        d["revenue_status"] = status(d["revenue_variance_pct"])
        d["ebit_status"] = status(d["ebit_variance_pct"])
        rows.append(d)
    return rows


def fetch_prev_month(client: bigquery.Client, period: date) -> list[dict]:
    """Pull the previous month, for a small trend indicator."""
    y, m = (period.year, period.month - 1) if period.month > 1 else (period.year - 1, 12)
    prev = date(y, m, 1)
    return fetch_month(client, prev)


def render(period: date, rows: list[dict], prev_rows: list[dict]) -> str:
    env = Environment(
        loader=FileSystemLoader(HERE / "templates"),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("kpi_report.html")

    # Build a prev-row lookup so the template can show trend arrows
    prev_by_brand = {r["brand_key"]: r for r in prev_rows}

    return template.render(
        period=period,
        rows=rows,
        prev=prev_by_brand,
        generated_at=date.today().isoformat(),
    )


def upload_to_gcs(html: str, path: str) -> None:
    client = storage.Client(project=PROJECT)
    bucket = client.bucket(BUCKET)
    blob = bucket.blob(path)
    blob.upload_from_string(html, content_type="text/html; charset=utf-8")
    print(f"uploaded to gs://{BUCKET}/{path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=str, help="ISO date of first day of month, e.g. 2026-05-01")
    ap.add_argument("--upload", action="store_true", help="also upload to GCS")
    ap.add_argument("--out", type=str, default="serving/output/index.html")
    args = ap.parse_args()

    client = bigquery.Client(project=PROJECT)

    period = date.fromisoformat(args.period) if args.period else latest_period(client)
    print(f"rendering {period}")

    rows = fetch_month(client, period)
    prev = fetch_prev_month(client, period)
    if not rows:
        raise SystemExit(f"no data for {period}")

    html = render(period, rows, prev)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({len(html):,} chars)")

    if args.upload:
        upload_to_gcs(html, "index.html")


if __name__ == "__main__":
    main()
