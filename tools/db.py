"""Read-only Postgres access for the agent-facing tool layer.

This module is the *only* place the tools talk to the database. It deliberately
exposes no way to run a free-form SQL string supplied by the model: callers pass
a parametrised statement that is defined in our own code (see ``tools/metrics.py``),
and every connection runs in a read-only transaction so a buggy or adversarial
query can never mutate the warehouse.

Connection target is taken from the ``DATABASE_URL`` environment variable and
falls back to the local docker-compose / cluster default used throughout the repo.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from contextlib import contextmanager
from typing import Any

import psycopg
from psycopg.rows import dict_row

DEFAULT_DATABASE_URL = "postgresql://hackathon:hackathon@localhost:5432/hotel_hackathon"


def database_url() -> str:
    """Return the configured Postgres connection string."""
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


@contextmanager
def connection():
    """Yield a psycopg connection pinned to a read-only transaction.

    A fresh connection per call keeps the tool layer simple and stateless; the
    work each tool does is a single short aggregate query, so pooling buys little
    and would add a dependency. The transaction is forced read-only as a hard
    guardrail against accidental writes from the analytics path.
    """
    conn = psycopg.connect(database_url(), row_factory=dict_row)
    try:
        conn.read_only = True
        conn.autocommit = False
        yield conn
        conn.rollback()
    finally:
        conn.close()


def query(sql: str, params: Sequence[Any] | dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Run a parametrised read-only query and return rows as dicts.

    ``sql`` is always a literal defined in our own modules; ``params`` carries the
    user-influenced values, bound safely by the driver. The model never supplies
    ``sql``.
    """
    with connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        if cur.description is None:
            return []
        return cur.fetchall()


def query_one(sql: str, params: Sequence[Any] | dict[str, Any] | None = None) -> dict[str, Any]:
    """Run a query expected to return a single row; return it (or an empty dict)."""
    rows = query(sql, params)
    return rows[0] if rows else {}
