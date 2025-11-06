"""
Database operations for IBTrACS updater
"""
import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql
from datetime import datetime
from typing import Optional
import json

from config import settings


def get_connection():
    """Get a PostgreSQL database connection"""
    return psycopg2.connect(settings.database_url)


def create_schema(conn):
    """
    Create the storms table if it doesn't exist.
    Each row represents a single track point (observation) for a storm.
    """
    with conn.cursor() as cur:
        cur.execute("""
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
        """)
        
        # Create index on time for efficient date queries
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_storms_time ON storms(time)
        """)
        
        # Create index on ID for efficient storm lookups
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_storms_id ON storms("ID")
        """)
        
        conn.commit()


def get_latest_track_date(conn) -> Optional[datetime]:
    """
    Get the latest track point date in the database.
    Returns None if the table is empty.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT MAX(time) FROM storms")
        result = cur.fetchone()[0]
        return result


def delete_storm_track_points(conn, storm_id: str, after_date: datetime):
    """
    Delete track points for a storm that are after a given date.
    This allows us to update a storm's track if new data is available.
    """
    with conn.cursor() as cur:
        cur.execute(
            'DELETE FROM storms WHERE "ID" = %s AND time > %s',
            (storm_id, after_date)
        )
        deleted = cur.rowcount
        conn.commit()
        return deleted


def insert_track_points(conn, track_points: list[dict]):
    """
    Insert track points into the database.
    track_points should be a list of dictionaries with keys matching table columns.
    """
    if not track_points:
        return 0
    
    columns = [
        'ID', 'ATCF_ID', 'name', 'basin', 'subbasin', 'season', 'genesis',
        'time', 'lat', 'lon', 'wind', 'mslp', 'speed', 'dist2land',
        'classification', 'rmw', 'basin_time', 'subbasin_time', 'agency',
        'R34_NE', 'R34_SE', 'R34_SW', 'R34_NW',
        'R50_NE', 'R50_SE', 'R50_SW', 'R50_NW',
        'R64_NE', 'R64_SE', 'R64_SW', 'R64_NW'
    ]
    
    # Prepare values for bulk insert
    values = []
    for point in track_points:
        row = tuple(point.get(col) for col in columns)
        values.append(row)
    
    with conn.cursor() as cur:
        # Use ON CONFLICT to handle duplicates ("ID", time is primary key)
        # Build the column list with proper quoting
        column_identifiers = sql.SQL(', ').join(map(sql.Identifier, columns))
        conflict_columns = sql.SQL(', ').join([sql.Identifier('ID'), sql.Identifier('time')])
        
        # Build the UPDATE SET clause with proper quoting
        update_parts = []
        for col in columns:
            if col == 'ID':  # Skip ID in UPDATE (it's in the conflict target)
                continue
            update_parts.append(
                sql.SQL("{} = EXCLUDED.{}").format(
                    sql.Identifier(col),
                    sql.Identifier(col)
                )
            )
        update_clause = sql.SQL(', ').join(update_parts)
        
        insert_query = sql.SQL("""
            INSERT INTO storms ({}) VALUES %s
            ON CONFLICT ({}) DO UPDATE SET
                {}
        """).format(column_identifiers, conflict_columns, update_clause)
        
        execute_values(cur, insert_query, values, page_size=1000)
        inserted = cur.rowcount
        conn.commit()
        return inserted

