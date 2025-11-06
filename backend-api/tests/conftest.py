"""
Pytest configuration and fixtures for testing
"""

import pytest
import sqlite3
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db


def get_test_db():
    """Test database dependency override"""
    conn = sqlite3.connect("tests/data/storms.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def client():
    """FastAPI test client with test database"""
    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()

