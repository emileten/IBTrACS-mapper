"""
Tests for the IBTrACS database updater
"""
import pytest
from datetime import datetime
from pathlib import Path

from database import (
    create_schema,
    get_latest_track_date,
    insert_track_points,
    get_connection
)
from csv_parser import parse_ibtracs_csv
# Import updater function in test that uses it to avoid issues


def test_schema_creation(clean_db):
    """Test that the database schema is created correctly"""
    create_schema(clean_db)
    
    with clean_db.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'storms'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        
        # Check that key columns exist
        column_names = [col[0] for col in columns]
        assert 'ID' in column_names
        assert 'time' in column_names
        assert 'lat' in column_names
        assert 'lon' in column_names
        assert 'name' in column_names


def test_empty_database_latest_date(clean_db):
    """Test that get_latest_track_date returns None for empty database"""
    create_schema(clean_db)
    latest = get_latest_track_date(clean_db)
    assert latest is None


def test_csv_parsing():
    """Test parsing of test CSV file"""
    test_csv = Path(__file__).parent.parent / "tests" / "data" / "ibtracs_sample.csv"
    
    if not test_csv.exists():
        pytest.skip(f"Test CSV not found at {test_csv}. Run scripts/create_test_data.py first.")
    
    track_points = parse_ibtracs_csv(str(test_csv))
    
    assert len(track_points) > 0, "Should parse at least some track points"
    
    # Check structure of first track point
    first_point = track_points[0]
    assert 'ID' in first_point
    assert 'time' in first_point
    assert 'lat' in first_point
    assert 'lon' in first_point
    assert isinstance(first_point['time'], datetime)


def test_incremental_update(clean_db):
    """Test incremental update logic"""
    create_schema(clean_db)
    
    # Insert some initial data
    initial_points = [
        {
            'ID': 'TEST001',
            'ATCF_ID': None,
            'name': 'TEST_STORM',
            'basin': 'NA',
            'subbasin': 'GM',
            'season': 2020,
            'genesis': datetime(2020, 1, 1, 0, 0),
            'time': datetime(2020, 1, 1, 0, 0),
            'lat': 20.0,
            'lon': -80.0,
            'wind': 30.0,
            'mslp': 1000.0,
            'speed': None,
            'dist2land': None,
            'classification': 'TS',
            'rmw': None,
            'basin_time': 'NA',
            'subbasin_time': 'GM',
            'agency': None,
            'R34_NE': None,
            'R34_SE': None,
            'R34_SW': None,
            'R34_NW': None,
            'R50_NE': None,
            'R50_SE': None,
            'R50_SW': None,
            'R50_NW': None,
            'R64_NE': None,
            'R64_SE': None,
            'R64_SW': None,
            'R64_NW': None,
        }
    ]
    
    insert_track_points(clean_db, initial_points)
    
    # Check latest date
    latest = get_latest_track_date(clean_db)
    assert latest == datetime(2020, 1, 1, 0, 0)
    
    # Parse CSV with start_date (should skip existing data)
    test_csv = Path(__file__).parent.parent / "tests" / "data" / "ibtracs_sample.csv"
    if test_csv.exists():
        track_points = parse_ibtracs_csv(str(test_csv), start_date=latest)
        # Should only get points after the initial date
        if track_points:
            for point in track_points:
                assert point['time'] > latest


def test_full_update(clean_db):
    """Test full database update with test CSV"""
    test_csv = Path(__file__).parent.parent / "tests" / "data" / "ibtracs_sample.csv"
    
    if not test_csv.exists():
        pytest.skip(f"Test CSV not found at {test_csv}. Run scripts/create_test_data.py first.")
    
    # Import here to avoid circular import - reload modules to pick up env var
    import importlib
    import config
    import database
    importlib.reload(config)
    importlib.reload(database)
    from updater import update_database
    
    # Run full update
    update_database(csv_path=str(test_csv))
    
    # Verify data was inserted
    latest = get_latest_track_date(clean_db)
    assert latest is not None
    
    # Check row count
    with clean_db.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM storms")
        count = cur.fetchone()[0]
        assert count > 0, "Should have inserted some track points"

