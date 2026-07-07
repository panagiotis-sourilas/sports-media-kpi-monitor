"""Load the three raw CSVs into BigQuery.

Idempotent — drops and recreates the target tables each run.
For dev only. Production loaders live upstream (SAP export, GA4 export, etc).
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from google.cloud import bigquery

PROJECT = os.environ.get("GCP_PROJECT_ID", "inc-182120-panagiotis-sourilas")
DATASET = os.environ.get("BQ_DATASET", "sports_media_kpi_monitor_dev")

# Table schemas — matches the generator's output. If the generator changes shape,
# these break loudly.
SCHEMAS: dict[str, list[bigquery.SchemaField]] = {
    "raw_financial": [
        bigquery.SchemaField("period",       "DATE",   mode="REQUIRED"),
        bigquery.SchemaField("brand_key",    "STRING", mode="REQUIRED"),
        bigquery.SchemaField("country",      "STRING", mode="REQUIRED"),
        bigquery.SchemaField("currency",     "STRING", mode="REQUIRED"),
        bigquery.SchemaField("pl_line",      "STRING", mode="REQUIRED"),
        bigquery.SchemaField("pl_category",  "STRING", mode="REQUIRED"),
        bigquery.SchemaField("amount",       "FLOAT",  mode="REQUIRED"),
    ],
    "raw_budget": [
        bigquery.SchemaField("period",       "DATE",   mode="REQUIRED"),
        bigquery.SchemaField("brand_key",    "STRING", mode="REQUIRED"),
        bigquery.SchemaField("country",      "STRING", mode="REQUIRED"),
        bigquery.SchemaField("currency",     "STRING", mode="REQUIRED"),
        bigquery.SchemaField("pl_line",      "STRING", mode="REQUIRED"),
        bigquery.SchemaField("pl_category",  "STRING", mode="REQUIRED"),
        bigquery.SchemaField("amount",       "FLOAT",  mode="REQUIRED"),
    ],
    "raw_traffic": [
        bigquery.SchemaField("date",         "DATE",   mode="REQUIRED"),
        bigquery.SchemaField("brand_key",    "STRING", mode="REQUIRED"),
        bigquery.SchemaField("country",      "STRING", mode="REQUIRED"),
        bigquery.SchemaField("device",       "STRING", mode="REQUIRED"),
        bigquery.SchemaField("users",        "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("sessions",     "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("pageviews",    "INTEGER", mode="REQUIRED"),
    ],
}

# Which raw folder maps to which BQ table
SOURCES = {
    "financial": "raw_financial",
    "budget":    "raw_budget",
    "traffic":   "raw_traffic",
}


def ensure_dataset(client: bigquery.Client) -> None:
    dataset_ref = bigquery.Dataset(f"{PROJECT}.{DATASET}")
    dataset_ref.location = "EU"
    dataset_ref.description = "Dev warehouse for sports-media-kpi-monitor portfolio project"
    client.create_dataset(dataset_ref, exists_ok=True)
    print(f"dataset ready: {PROJECT}.{DATASET}")


def load_csv_to_table(client: bigquery.Client, csv_path: Path, table_name: str) -> None:
    table_id = f"{PROJECT}.{DATASET}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        schema=SCHEMAS[table_name],
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        # Partition traffic by day for cheap date-filter queries later
        time_partitioning=(
            bigquery.TimePartitioning(field="date")
            if table_name == "raw_traffic" else None
        ),
    )

    with csv_path.open("rb") as f:
        job = client.load_table_from_file(f, table_id, job_config=job_config)
    job.result()  # blocks until done

    table = client.get_table(table_id)
    print(f"loaded {table_id}: {table.num_rows} rows, {table.num_bytes:,} bytes")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=str, default="raw", help="path to the raw/ folder")
    args = ap.parse_args()

    raw = Path(args.raw)
    if not raw.exists():
        raise SystemExit(f"no raw/ folder at {raw}. run generate.py first.")

    client = bigquery.Client(project=PROJECT)
    ensure_dataset(client)

    for source, table_name in SOURCES.items():
        # find the most recent CSV in each source folder
        source_dir = raw / source
        csvs = sorted(source_dir.glob("*.csv"))
        if not csvs:
            print(f"no CSVs found in {source_dir}, skipping")
            continue
        latest = csvs[-1]
        load_csv_to_table(client, latest, table_name)


if __name__ == "__main__":
    main()
