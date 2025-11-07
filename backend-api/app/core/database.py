from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

from app.core.config import settings


@contextmanager
def _get_connection():
    conn = psycopg2.connect(settings.database_url, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


def get_db():
    """Dependency for database connection."""
    with _get_connection() as conn:
        yield conn

