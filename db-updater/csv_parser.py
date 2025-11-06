"""
Parser for IBTrACS CSV format
"""
import pandas as pd
from datetime import datetime
from typing import Optional
import numpy as np


def parse_float(value) -> Optional[float]:
    """Parse a value to float, returning None if invalid"""
    if pd.isna(value) or value == '' or value == -999:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_ibtracs_csv(csv_path: str, start_date: Optional[datetime] = None) -> list[dict]:
    """
    Parse IBTrACS CSV file and convert to track points.
    
    The IBTrACS CSV format has one row per track point (observation).
    Each row contains storm metadata and observation data for that time.
    
    Args:
        csv_path: Path to the IBTrACS CSV file
        start_date: Only include track points after this date (for incremental updates)
    
    Returns:
        List of track point dictionaries ready for database insertion
    """
    print(f"Reading CSV file: {csv_path}")
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"Loaded {len(df)} rows from CSV")
    
    # Convert ISO_TIME to datetime
    df['ISO_TIME'] = pd.to_datetime(df['ISO_TIME'], errors='coerce')
    
    # Filter by start_date if provided (for incremental updates)
    if start_date:
        df = df[df['ISO_TIME'] > start_date].copy()
        print(f"Filtered to {len(df)} rows after {start_date}")
    
    # Remove rows with invalid time or missing lat/lon
    df = df[df['ISO_TIME'].notna()].copy()
    df = df[df['LAT'].notna()].copy()
    df = df[df['LON'].notna()].copy()
    
    # Calculate genesis time for each storm (minimum ISO_TIME per SID)
    # We need to do this before processing individual rows
    genesis_times = df.groupby('SID')['ISO_TIME'].min().to_dict()
    
    track_points = []
    
    # Process each row (each row is already a track point)
    for idx, row in df.iterrows():
        storm_id = str(row.get('SID', ''))
        if not storm_id or storm_id == 'nan':
            continue
        
        storm_name = str(row.get('NAME', 'NOT_NAMED'))
        if storm_name == 'nan' or pd.isna(row.get('NAME')):
            storm_name = 'NOT_NAMED'
        
        # Get ATCF_ID if available (check multiple possible column names)
        atcf_id = None
        for col in ['USA_ATCF_ID', 'ATCF_ID']:
            if col in row and pd.notna(row.get(col)):
                atcf_id_val = str(row.get(col))
                if atcf_id_val and atcf_id_val != 'nan':
                    atcf_id = atcf_id_val
                    break
        
        basin = str(row.get('BASIN', ''))
        subbasin = str(row.get('SUBBASIN', ''))
        season = int(row.get('SEASON', 0)) if pd.notna(row.get('SEASON')) else 0
        
        # Get genesis time (earliest time for this storm)
        genesis = genesis_times.get(storm_id)
        if genesis is None:
            genesis = row['ISO_TIME']
        
        # Get observation time
        point_time = row['ISO_TIME']
        if pd.isna(point_time):
            continue
        
        # Build track point
        track_point = {
            'ID': storm_id,
            'ATCF_ID': atcf_id,
            'name': storm_name,
            'basin': basin,
            'subbasin': subbasin,
            'season': season,
            'genesis': genesis.to_pydatetime() if hasattr(genesis, 'to_pydatetime') else genesis,
            'time': point_time.to_pydatetime() if hasattr(point_time, 'to_pydatetime') else point_time,
            'lat': parse_float(row.get('LAT')),
            'lon': parse_float(row.get('LON')),
            'wind': parse_float(row.get('USA_WIND')),
            'mslp': parse_float(row.get('USA_PRES')),
            'speed': None,  # STORM_SPEED not in standard columns
            'dist2land': parse_float(row.get('DIST2LAND')),
            'classification': str(row.get('USA_STATUS', '')) if pd.notna(row.get('USA_STATUS')) else None,
            'rmw': parse_float(row.get('USA_RMW')),
            'basin_time': str(row.get('BASIN', '')) if pd.notna(row.get('BASIN')) else basin,
            'subbasin_time': str(row.get('SUBBASIN', '')) if pd.notna(row.get('SUBBASIN')) else subbasin,
            'agency': str(row.get('USA_AGENCY', '')) if pd.notna(row.get('USA_AGENCY')) else None,
            'R34_NE': parse_float(row.get('USA_R34_NE')),
            'R34_SE': parse_float(row.get('USA_R34_SE')),
            'R34_SW': parse_float(row.get('USA_R34_SW')),
            'R34_NW': parse_float(row.get('USA_R34_NW')),
            'R50_NE': parse_float(row.get('USA_R50_NE')),
            'R50_SE': parse_float(row.get('USA_R50_SE')),
            'R50_SW': parse_float(row.get('USA_R50_SW')),
            'R50_NW': parse_float(row.get('USA_R50_NW')),
            'R64_NE': parse_float(row.get('USA_R64_NE')),
            'R64_SE': parse_float(row.get('USA_R64_SE')),
            'R64_SW': parse_float(row.get('USA_R64_SW')),
            'R64_NW': parse_float(row.get('USA_R64_NW')),
        }
        
        # Only add if we have valid lat/lon
        if track_point['lat'] is not None and track_point['lon'] is not None:
            track_points.append(track_point)
    
    print(f"Parsed {len(track_points)} track points")
    return track_points

