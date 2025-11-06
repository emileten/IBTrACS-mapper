import sqlite3
from app.core.config import settings


def get_db():
    """Dependency for database connection"""
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row  # Makes rows accessible by column name
    try:
        yield conn
    finally:
        conn.close()

