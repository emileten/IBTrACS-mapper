"""Pytest configuration and fixtures for PostgreSQL-backed testing."""

from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Iterable

import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
import pytest
from fastapi.testclient import TestClient

# Ensure the backend uses the local PostgreSQL instance during tests
os.environ.setdefault("DATABASE_URL", "postgresql://ibtracs:ibtracs_dev@localhost:5432/ibtracs")

from app.core.config import settings
from app.core.database import get_db
from app.main import app


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS storms (
    "ID" VARCHAR(50) NOT NULL,
    "ATCF_ID" VARCHAR(50),
    name VARCHAR(100) NOT NULL,
    basin VARCHAR(10) NOT NULL,
    subbasin VARCHAR(10) NOT NULL,
    season INTEGER NOT NULL,
    genesis TIMESTAMP NOT NULL,
    time TIMESTAMP NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    wind DOUBLE PRECISION,
    mslp DOUBLE PRECISION,
    speed DOUBLE PRECISION,
    dist2land DOUBLE PRECISION,
    classification VARCHAR(10),
    rmw DOUBLE PRECISION,
    basin_time VARCHAR(10),
    subbasin_time VARCHAR(10),
    agency VARCHAR(50),
    "R34_NE" DOUBLE PRECISION,
    "R34_SE" DOUBLE PRECISION,
    "R34_SW" DOUBLE PRECISION,
    "R34_NW" DOUBLE PRECISION,
    "R50_NE" DOUBLE PRECISION,
    "R50_SE" DOUBLE PRECISION,
    "R50_SW" DOUBLE PRECISION,
    "R50_NW" DOUBLE PRECISION,
    "R64_NE" DOUBLE PRECISION,
    "R64_SE" DOUBLE PRECISION,
    "R64_SW" DOUBLE PRECISION,
    "R64_NW" DOUBLE PRECISION,
    PRIMARY KEY ("ID", time)
)
"""


INSERT_COLUMNS = (
    "ID", "ATCF_ID", "name", "basin", "subbasin", "season",
    "genesis", "time", "lat", "lon", "wind", "mslp", "speed",
    "dist2land", "classification", "rmw", "basin_time", "subbasin_time",
    "agency", "R34_NE", "R34_SE", "R34_SW", "R34_NW", "R50_NE",
    "R50_SE", "R50_SW", "R50_NW", "R64_NE", "R64_SE", "R64_SW",
    "R64_NW"
)

INSERT_COLUMNS_SQL = ", ".join(f'"{col}"' for col in INSERT_COLUMNS)
INSERT_SQL = f"INSERT INTO storms ({INSERT_COLUMNS_SQL}) VALUES %s"


SAMPLE_TRACK = [
    (
        "2020080N00001",
        "AL012020",
        "ALPHA",
        "NA",
        "GM",
        2020,
        datetime(2020, 8, 1, 0, 0),
        datetime(2020, 8, 1, 0, 0),
        25.0,
        -75.0,
        40.0,
        1002.0,
        None,
        None,
        "TS",
        None,
        "NA",
        "GM",
        "hurdat_atl",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),
    (
        "2020080N00001",
        "AL012020",
        "ALPHA",
        "NA",
        "GM",
        2020,
        datetime(2020, 8, 1, 6, 0),
        datetime(2020, 8, 1, 6, 0),
        26.0,
        -74.0,
        45.0,
        1000.0,
        None,
        None,
        "TS",
        None,
        "NA",
        "GM",
        "hurdat_atl",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ),
]


def _wait_for_database(max_retries: int = 30, delay: float = 1.0) -> None:
    for attempt in range(max_retries):
        try:
            with psycopg2.connect(settings.database_url, connect_timeout=2):
                return
        except psycopg2.OperationalError:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay)


def _reset_database(sample_rows: Iterable[tuple]) -> None:
    conn = psycopg2.connect(settings.database_url)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS storms CASCADE")
                cur.execute(CREATE_TABLE_SQL)
                execute_values(cur, INSERT_SQL, sample_rows)
    finally:
        conn.close()


@pytest.fixture(scope="session", autouse=True)
def prepare_database() -> None:
    _wait_for_database()
    _reset_database(SAMPLE_TRACK)


def get_test_db():
    conn = psycopg2.connect(settings.database_url, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def client():
    """FastAPI test client backed by a seeded PostgreSQL database."""

    app.dependency_overrides[get_db] = get_test_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()

