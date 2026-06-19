"""Seed a local Postgres with a self-contained demo dataset.

This is the no-dependencies way to run the project: it applies the schema, the
rate-plan FK override, and the semantic views, then loads a small deterministic
dataset, with no scrape and no external data source required. The dataset is the
same one that backs the test suite (`tests/fixture_data.py`), so there is a single
source of truth; it is hand-built to exercise every scenario the agent reasons about
(multi-night and multi-room stays, cancellations, provisional business, OTA
concentration, an effective-vs-static macro-group reclassification, group/block vs
transient, and point-in-time differences).

Usage:
    export DATABASE_URL=postgresql://revenue:revenue@localhost:5432/hotel_revenue
    uv run python -m scripts.seed_demo

The stay dates sit in 2025; ask the agent about those months explicitly (e.g.
"the on-the-books summary for August 2025") since it resolves bare "this month"
against the real current date. For production, the Playwright ETL (`etl/run_etl.py`)
loads the same tables from the live source system instead.
"""

from __future__ import annotations

import os
from pathlib import Path

import psycopg

SOLUTION_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = SOLUTION_ROOT / "sql"


def _database_url() -> str:
    return os.environ.get(
        "DATABASE_URL", "postgresql://revenue:revenue@localhost:5432/hotel_revenue"
    )


def _apply_schema(conn: psycopg.Connection) -> None:
    """Apply schema, the FK override, and the semantic views (all idempotent)."""
    schema_sql = (SOLUTION_ROOT / "schema.sql").read_text(encoding="utf-8")
    overrides_sql = (SQL_DIR / "schema_overrides.sql").read_text(encoding="utf-8")
    views_sql = (SQL_DIR / "views.sql").read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(schema_sql)
        cur.execute(overrides_sql)
        cur.execute(views_sql)
    conn.commit()


def _load(conn: psycopg.Connection) -> None:
    """Truncate and reload every lookup, the fact table, and a stub load_manifest row."""
    from tests.fixture_data import (
        CHANNELS,
        MACRO_HISTORY,
        MARKET_CODES,
        RATE_PLANS,
        ROOM_TYPES,
        all_reservation_rows,
    )

    with conn.cursor() as cur:
        cur.execute(
            "truncate reservations, market_macro_group_history, "
            "room_type_lookup, rate_plan_lookup, market_code_lookup, "
            "channel_code_lookup, load_manifest restart identity cascade"
        )
        cur.executemany(
            "insert into room_type_lookup(space_type, room_class, display_name, number_of_rooms)"
            " values (%s,%s,%s,%s)",
            ROOM_TYPES,
        )
        cur.executemany(
            "insert into rate_plan_lookup(rate_plan_code, plan_family, is_commissionable)"
            " values (%s,%s,%s)",
            RATE_PLANS,
        )
        cur.executemany(
            "insert into market_code_lookup(market_code, market_name, macro_group, description)"
            " values (%s,%s,%s,%s)",
            MARKET_CODES,
        )
        cur.executemany(
            "insert into market_macro_group_history(market_code, valid_from, valid_to, macro_group)"
            " values (%s,%s,%s,%s)",
            MACRO_HISTORY,
        )
        cur.executemany(
            "insert into channel_code_lookup(channel_code, channel_name, channel_group)"
            " values (%s,%s,%s)",
            CHANNELS,
        )

        rows = all_reservation_rows()
        cols = list(rows[0].keys())
        placeholders = ", ".join(f"%({c})s" for c in cols)
        collist = ", ".join(cols)
        cur.executemany(
            f"insert into reservations ({collist}) values ({placeholders})",
            rows,
        )
        cur.execute(
            "insert into load_manifest(dataset_revision, scraped_at, source_url, row_hash)"
            " values (%s, now(), %s, %s)",
            ("demo-seed", "https://example.test/demo", "demo"),
        )
    conn.commit()


def main() -> None:
    url = _database_url()
    with psycopg.connect(url) as conn:
        _apply_schema(conn)
        _load(conn)
        with conn.cursor() as cur:
            cur.execute("select count(distinct reservation_id), count(*) from reservations")
            reservations, stay_rows = cur.fetchone()
    print(
        f"Seeded {reservations} reservations across {stay_rows} stay-night rows into {url}"
    )


if __name__ == "__main__":
    main()
