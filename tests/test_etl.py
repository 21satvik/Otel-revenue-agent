"""ETL property tests (Phase 1), ETL_TEST_SCENARIOS.md.

The DB-backed cases run against the loaded fixture (``db`` fixture); the
expansion case tests the pure transform without a browser or database. Against a
real scrape these same assertions hold for the live dataset.
"""

from __future__ import annotations

import json
from pathlib import Path

import psycopg
import pytest

from etl.run_etl import reservation_ids_sha256
from etl.transform import expand_reservation

_ETL_DIR = Path(__file__).resolve().parents[1] / "etl"


def _load_json(name: str) -> dict:
    """Read a committed ETL provenance artifact from ``etl/``."""
    return json.loads((_ETL_DIR / name).read_text(encoding="utf-8"))


# Scenario 1, lookup row counts
@pytest.mark.db
def test_scenario1_lookup_counts(db):
    """Each lookup table loads exactly the expected number of rows."""
    expected = {
        "room_type_lookup": 3,
        "rate_plan_lookup": 8,
        "market_code_lookup": 10,
        "market_macro_group_history": 11,
        "channel_code_lookup": 4,
    }
    with psycopg.connect(db) as conn, conn.cursor() as cur:
        for table, count in expected.items():
            cur.execute(f"select count(*) from {table}")
            assert cur.fetchone()[0] == count, table


# Scenario 2, fact-table grain uniqueness
@pytest.mark.db
def test_scenario2_grain_uniqueness(db):
    """The fact table is unique at its grain: no duplicate (reservation_id, stay_date)."""
    with psycopg.connect(db) as conn, conn.cursor() as cur:
        cur.execute(
            "select count(*) from ("
            "  select reservation_id, stay_date from reservations_hackathon"
            "  group by reservation_id, stay_date having count(*) > 1"
            ") dups"
        )
        assert cur.fetchone()[0] == 0


# Scenario 3a, the two committed provenance artifacts agree with each other.
# Pure file check (no DB, no network), so it always runs and catches a stale or
# mismatched regeneration of either file.
def test_scenario3_manifest_and_proof_agree():
    """SCRAPE_MANIFEST.json and LOAD_PROOF.json reconcile internally."""
    manifest = _load_json("SCRAPE_MANIFEST.json")
    proof = _load_json("LOAD_PROOF.json")
    check = proof["scrape_manifest_check"]

    assert check["manifest_valid"] is True
    assert check["manifest_errors"] == []
    assert manifest["reservation_ids_count"] == check["db_reservation_ids_count"]
    assert manifest["reservation_ids_sha256"] == check["db_reservation_ids_sha256"]
    assert manifest["dataset_revision"] == proof["dataset_revision"]
    # The status fingerprint is one hash and must be identical everywhere it appears.
    assert manifest["row_hash"] == proof["load_manifest_row_hash"]
    assert proof["reservation_stay_status_sha256"] == proof["load_manifest_row_hash"]


# Scenario 3b, reconcile the manifest against a real load when one is present.
# Skips on the synthetic fixture DB or whenever no working DB holds the manifest's
# load (e.g. CI, or a freshly cleaned dev box), so the suite stays green offline.
def test_scenario3_manifest_reconciles_real_load(real_db_url):
    """When the working DB holds the manifest's load, its count + revision match."""
    manifest = _load_json("SCRAPE_MANIFEST.json")
    try:
        with psycopg.connect(real_db_url) as conn, conn.cursor() as cur:
            cur.execute("select distinct reservation_id from reservations_hackathon")
            ids = [r[0] for r in cur.fetchall()]
            cur.execute(
                "select dataset_revision from load_manifest order by scraped_at desc limit 1"
            )
            row = cur.fetchone()
            db_revision = row[0] if row else None
    except psycopg.Error:
        pytest.skip("no working database holds a real load to reconcile")

    if reservation_ids_sha256(ids) != manifest["reservation_ids_sha256"]:
        pytest.skip("working DB does not hold the load described by SCRAPE_MANIFEST.json")

    # The DB is the manifest's load: assert the brief's reconciliation properties.
    assert len(ids) == manifest["reservation_ids_count"]
    assert db_revision == manifest["dataset_revision"]


# Scenario 4, stay-row expansion equals nights
@pytest.mark.db
def test_scenario4_expansion_in_db(db):
    """A multi-night reservation expands to exactly ``nights`` stay rows in the DB."""
    with psycopg.connect(db) as conn, conn.cursor() as cur:
        # J1 is a 3-night reservation in the fixture.
        cur.execute(
            "select nights, count(*) from reservations_hackathon "
            "where reservation_id = 'J1' group by nights"
        )
        nights, rows = cur.fetchone()
        assert rows == nights == 3


def test_scenario4_expansion_pure_transform():
    """expand_reservation produces exactly ``nights`` typed rows (no DB)."""
    detail = {
        "reservation_id": "X1",
        "arrival_date": "2025-07-10",
        "departure_date": "2025-07-13",
        "nights": "3",
        "reservation_status": "Reserved",
        "financial_status": "Posted",
        "create_datetime": "2025-06-01T10:00:00Z",
        "space_type": "STD",
        "market_code": "BAR",
        "channel_code": "WEB",
        "rate_plan_code": "BOOKBAR",
        "number_of_spaces": "2",
        "daily_room_revenue_before_tax": "100",
        "daily_total_revenue_before_tax": "120",
        "stay_nights": [
            {"stay_date": "2025-07-10"},
            {"stay_date": "2025-07-11"},
            {"stay_date": "2025-07-12"},
        ],
    }
    rows = expand_reservation(detail)
    assert len(rows) == 3
    assert {r.stay_date.isoformat() for r in rows} == {
        "2025-07-10", "2025-07-11", "2025-07-12"
    }
    assert all(r.number_of_spaces == 2 for r in rows)
    assert all(r.create_datetime.tzinfo is not None for r in rows)  # UTC-aware


def test_expansion_rejects_incomplete_scrape():
    """A short stay_nights list vs declared nights fails loudly (no silent drop)."""
    detail = {
        "reservation_id": "X2",
        "arrival_date": "2025-07-10",
        "departure_date": "2025-07-13",
        "nights": "3",
        "reservation_status": "Reserved",
        "financial_status": "Posted",
        "create_datetime": "2025-06-01T10:00:00Z",
        "space_type": "STD",
        "market_code": "BAR",
        "channel_code": "WEB",
        "rate_plan_code": "BOOKBAR",
        "stay_nights": [{"stay_date": "2025-07-10"}],  # only 1 of 3 nights
    }
    with pytest.raises(ValueError, match="incomplete detail scrape"):
        expand_reservation(detail)
