#!/usr/bin/env python3
"""Apply the post-schema DDL to the database in DATABASE_URL.

Runs, in order, after schema.sql exists (docker compose up / cluster init):
sql/schema_overrides.sql (the one documented FK relaxation) then sql/views.sql
(the semantic views). Idempotent: the override uses DROP ... IF EXISTS and every
view is CREATE OR REPLACE VIEW.
"""

from __future__ import annotations

import sys
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.db import database_url  # noqa: E402

SQL_DIR = Path(__file__).resolve().parents[1] / "sql"
# Applied in order: overrides (FK relaxation) before the views that read the tables.
DDL_FILES = ["schema_overrides.sql", "views.sql"]


def main() -> int:
    """Apply each DDL file in order within one transaction; print what was applied."""
    with psycopg.connect(database_url()) as conn:
        with conn.cursor() as cur:
            for name in DDL_FILES:
                cur.execute((SQL_DIR / name).read_text(encoding="utf-8"))
        conn.commit()
    print(f"Applied {', '.join(DDL_FILES)} to {database_url().split('@')[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
