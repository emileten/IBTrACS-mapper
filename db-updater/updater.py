"""
IBTrACS Database Updater

This script fetches the latest IBTrACS archive data and updates the database.
It runs daily to keep the database synchronized with the IBTrACS archive.
"""
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
import requests
from tqdm import tqdm

from config import settings
from database import (
    get_connection,
    create_schema,
    get_latest_track_date,
    delete_storm_track_points,
    insert_track_points
)
from csv_parser import parse_ibtracs_csv


def download_csv(url: str, output_path: str) -> str:
    """
    Download the IBTrACS CSV file.
    
    Args:
        url: URL to download from
        output_path: Path to save the file
    
    Returns:
        Path to the downloaded file
    """
    print(f"Downloading IBTrACS CSV from {url}...")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(output_path, 'wb') as f, tqdm(
        desc="Downloading",
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                pbar.update(len(chunk))
    
    print(f"Downloaded to {output_path}")
    return output_path


def update_database(csv_path: str = None):
    """
    Main function to update the IBTrACS database.
    
    Args:
        csv_path: Optional path to CSV file. If None, downloads from URL.
    
    This function:
    1. Fetches the latest IBTrACS archive data (or uses provided CSV)
    2. Processes and validates the data
    3. Updates the database with new/changed records
    """
    print(f"[{datetime.now()}] Starting IBTrACS database update...")
    
    # Connect to database
    print(f"Connecting to database...")
    conn = get_connection()
    
    try:
        # Create schema if it doesn't exist
        print("Creating/verifying database schema...")
        create_schema(conn)
        
        # Get latest track date for incremental updates
        latest_date = get_latest_track_date(conn)
        if latest_date:
            print(f"Latest track point in database: {latest_date}")
            print("Performing incremental update (only new data)...")
        else:
            print("Database is empty. Performing full import...")
        
        # Download or use provided CSV
        if csv_path is None:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as tmp:
                csv_path = tmp.name
            try:
                download_csv(settings.IBTRACS_CSV_URL, csv_path)
            except Exception as e:
                os.unlink(csv_path)
                raise Exception(f"Failed to download CSV: {e}")
        
        # Parse CSV
        print("Parsing CSV file...")
        track_points = parse_ibtracs_csv(csv_path, start_date=latest_date)
        
        if not track_points:
            print("No new track points to add.")
            return
        
        print(f"Found {len(track_points)} new track points to insert")
        
        # Group track points by storm ID for potential updates
        storms_to_update = {}
        for point in track_points:
            storm_id = point['ID']
            if storm_id not in storms_to_update:
                storms_to_update[storm_id] = []
            storms_to_update[storm_id].append(point)
        
        # For storms that have new data, delete existing points after latest_date
        # This handles cases where a storm's track is updated
        if latest_date:
            print("Cleaning up updated storm tracks...")
            for storm_id, points in storms_to_update.items():
                # Get the earliest new point date for this storm
                min_new_date = min(p['time'] for p in points)
                if min_new_date <= latest_date:
                    # This storm has updates, delete points after latest_date
                    deleted = delete_storm_track_points(conn, storm_id, latest_date)
                    if deleted > 0:
                        print(f"  Deleted {deleted} old track points for storm {storm_id}")
        
        # Insert new track points
        print("Inserting track points into database...")
        inserted = insert_track_points(conn, track_points)
        print(f"Inserted/updated {inserted} track points")
        
        # Clean up temporary file if we downloaded it
        if csv_path and not os.path.exists(csv_path):
            # It was a temp file, try to clean it up
            try:
                if os.path.exists(csv_path):
                    os.unlink(csv_path)
            except:
                pass
        
        print(f"[{datetime.now()}] Database update completed successfully.")
        
    except Exception as e:
        print(f"Error updating database: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Update IBTrACS database")
    parser.add_argument(
        "--csv",
        type=str,
        help="Path to CSV file (if not provided, downloads from URL)"
    )
    
    args = parser.parse_args()
    update_database(csv_path=args.csv)
