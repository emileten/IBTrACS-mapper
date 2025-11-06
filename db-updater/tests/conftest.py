"""
Pytest configuration for db-updater tests
"""
import pytest
import psycopg2
import os
import subprocess
import time
from pathlib import Path

from config import Settings


@pytest.fixture(scope="session")
def test_db():
    """
    Create a test database using Docker Compose (for local) or GitHub Actions service (for CI).
    This fixture starts the database at the beginning of the test session
    and stops it at the end.
    
    IMPORTANT: In CI (GitHub Actions), we use the service container, NOT Docker Compose.
    This avoids Docker-in-Docker (DinD) issues.
    """
    # Check if we're in CI (GitHub Actions provides a service)
    # Check multiple CI indicators to be safe
    is_ci = (
        os.getenv("CI") == "true" or
        os.getenv("GITHUB_ACTIONS") == "true" or
        os.getenv("GITHUB_ACTION") is not None
    )
    
    db_dir = None  # Only used for local Docker Compose cleanup
    
    if is_ci:
        # In CI: Use GitHub Actions service container (no Docker Compose)
        # The service is already running and available at localhost:5432
        print("CI environment detected: Using GitHub Actions PostgreSQL service (no Docker Compose)")
    else:
        # Local development: use Docker Compose
        db_dir = Path(__file__).parent.parent
        
        # Check if Docker is available
        try:
            subprocess.run(
                ["docker", "info"],
                check=True,
                capture_output=True,
                timeout=5
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Docker is not running. Please start Docker/OrbStack to run database tests.")
        
        # Start Docker Compose
        print("Local environment: Starting test database with Docker Compose...")
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=db_dir,
            check=False,
            capture_output=True
        )
        if result.returncode != 0:
            pytest.skip(f"Failed to start Docker Compose: {result.stderr.decode()}")
    
    # Wait for database to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                "postgresql://ibtracs:ibtracs_dev@localhost:5432/ibtracs"
            )
            conn.close()
            break
        except psycopg2.OperationalError:
            if i < max_retries - 1:
                time.sleep(1)
            else:
                raise
    
    yield
    
    if not is_ci and db_dir is not None:
        # Clean up: stop Docker Compose (only in local, never in CI)
        print("Stopping test database (Docker Compose)...")
        subprocess.run(
            ["docker-compose", "down", "-v"],
            cwd=db_dir,
            check=False,
            capture_output=True
        )


@pytest.fixture
def db_connection(test_db):
    """Get a database connection for testing"""
    # Set USE_LOCAL_DB for config
    os.environ["USE_LOCAL_DB"] = "true"
    
    conn = psycopg2.connect(
        "postgresql://ibtracs:ibtracs_dev@localhost:5432/ibtracs"
    )
    yield conn
    conn.close()


@pytest.fixture
def clean_db(db_connection):
    """Clean the database before each test"""
    with db_connection.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS storms CASCADE")
        db_connection.commit()
    yield db_connection

